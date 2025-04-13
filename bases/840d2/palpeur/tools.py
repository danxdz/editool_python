import os
import re

import math # Ensure math is imported

from constants import BASE_PATH


# --- Helper Functions ---

def find_label_forward(content, label, start_index, status_callback):
    pat = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for i in range(start_index + 1, len(content)):
        if pat.match(content[i].strip()): return i
    status_callback(f"⚠️ Lbl {label} Fwd Fail"); return len(content)

def find_label_backward(content, label, start_index, status_callback):
    pat = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for i in range(start_index - 1, -1, -1):
        if pat.match(content[i].strip()): return i
    status_callback(f"⚠️ Lbl {label} Bwd Fail"); return len(content)

def find_label_any(content, label, status_callback):
    pat = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for i, line in enumerate(content):
        if pat.match(line.strip()): return i
    status_callback(f"⚠️ Lbl {label} Any Fail"); return len(content)


def extract_movements(code_line):
    """Extracts G-code movement commands and coordinates."""
    g_codes = re.findall(r'\bG([0-4])\b', code_line) # G0-G4
    desc = {'G0':'Rapid','G1':'Linear','G2':'CW Arc','G3':'CCW Arc','G4':'Dwell'}
    coords = re.findall(r'([XYZABCUVW])([-+]?\d*\.?\d+)', code_line, re.IGNORECASE)
    coord_str = " ".join([f"{ax}{val}" for ax, val in coords])
    return [f"G{gc} ({desc.get(f'G{gc}', '?')}) {coord_str}".strip() for gc in g_codes]


def read_file(name, status_callback):
    """Reads NC program file, trying different encodings."""
    path = os.path.join(BASE_PATH, f"{name}.nc")
    if not os.path.isfile(path): status_callback(f"❌ File not found: {path}"); return None
    encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'latin-1']; last_error = None
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f: content = f.readlines()
            status_callback(f"📂 Loaded: {path} ({enc})"); return content
        except UnicodeDecodeError as e: last_error = e; continue
        except Exception as e: status_callback(f"❌ Read Error {path}: {e}"); return None
    status_callback(f"❌ Decode Fail {path}. Last: {last_error}"); return None


def bind_arguments(args_list, target_vars, status_callback, is_subcall=False):
    if args_list is None: return target_vars
    for i, arg in enumerate(args_list):
        bp, sp = f"BP_{i+1}", f"$P_SUBPAR[{i+1}]"
        if arg is not None: target_vars[bp], target_vars[sp] = str(arg), "1"
        else: target_vars[bp], target_vars[sp] = "0", "0"
    return target_vars

def parse_call(call_str):
    """Parses BPxxxx(...) calls, returning func_name, args_list, error_msg."""
    match = re.match(r"(BP\d+)\s*\((.*)\)", call_str.strip())
    if not match: return None, None, f"Invalid format: {call_str}";
    func = match.group(1).upper(); args_str = match.group(2).strip()
    args = [] if not args_str else [a.strip() if a.strip() else None for a in args_str.split(',')]
    return func, args, None

def _try_numerical(val_str):
    """Attempt conversion to float, return original string if failed."""
    if val_str is None: return None
    try: return float(val_str)
    except (ValueError, TypeError): return str(val_str)

# --- REVISED update_variables: Ensure Array Index is Int ---
def update_variables(line, variables, status_callback):
    """Processes an assignment line VAR[IDX] = expression."""
    match = re.match(r"\s*([\w$]+)(?:\[(.*?)\])?\s*=\s*(.*)", line.strip(), re.IGNORECASE)
    if match:
        var_base, index_part, expr_str = match.groups()
        var_base = var_base.upper()
        var_name_key = var_base # Default key

        if index_part is not None: # Array assignment
            try:
                index_val_str = evaluate_expression(index_part, variables, status_callback, True)
                index_val = int(float(index_val_str)) # Ensure int index
                var_name_key = f"{var_base}[{index_val}]" # Construct key like BP_R_QS3[2]
                # status_callback(f"DEBUG: Array Assign Key: {var_name_key}") # Verbose Debug
            except Exception as e:
                status_callback(f"⚠️ Assign Idx Err {var_base}[{index_part}]: {e}")
                return variables # Skip if index bad
        # else: simple assignment, var_name_key is already var_base

        value = evaluate_expression(expr_str, variables, status_callback) # Evaluate RHS
        variables[var_name_key] = str(value) # Store result as string
        # status_callback(f" Assign: {var_name_key} = {value}") # Reduce log noise
    return variables


# --- REVISED evaluate_expression: Add TRUNC ---
def evaluate_expression(expr_str, variables, status_callback, is_sub_eval=False):
    """Evaluates NC expressions with substitutions, comments, and basic math."""
    if expr_str is None: return "0"
    processed_expr = str(expr_str).strip()
    processed_expr = processed_expr.split(';', 1)[0].strip() # Strip comments FIRST
    if not processed_expr: return "0"
    axis_match = re.match(r"^\s*\(([XYZABCUVW]\d*)\)\s*$", processed_expr, re.IGNORECASE)
    if axis_match: return axis_match.group(1).upper() # Return axis name string

    # Function handling
    def handle_func(match):
         func_name = match.group(1).upper(); func_arg_str = match.group(2)
         arg_val_str = evaluate_expression(func_arg_str, variables, status_callback, True) # Recursive eval for arg
         try:
              arg_val_num = float(arg_val_str) # Functions usually need numeric args
              if func_name == 'ABS': return str(abs(arg_val_num))
              if func_name == 'ROUND': return str(round(arg_val_num))
              if func_name == 'SQRT': return str(math.sqrt(arg_val_num))
              if func_name == 'SIN': return str(math.sin(math.radians(arg_val_num)))
              if func_name == 'COS': return str(math.cos(math.radians(arg_val_num)))
              if func_name == 'TRUNC': return str(math.trunc(arg_val_num)) # Added TRUNC
              else: return match.group(0) # Unknown func, return original text
         except ValueError: # Handle case where arg is not a number after evaluation
             if func_name == 'TRUNC': return "0" # TRUNC of non-number might be 0
             if not is_sub_eval: status_callback(f"⚠️ Func Err {func_name}({arg_val_str}): Arg not number")
             return match.group(0) # Return original text
         except Exception as e:
              if not is_sub_eval: status_callback(f"⚠️ Func Err {func_name}({arg_val_str}): {e}")
              return match.group(0)
    # Update regex to include TRUNC
    processed_expr = re.sub(r"\b(ABS|ROUND|SQRT|SIN|COS|TRUNC)\s*\(\s*(.*?)\s*\)", handle_func, processed_expr, flags=re.IGNORECASE)

    # Array variable substitution (ensure index is int)
    def replace_array_var_expr(match):
        var_name = match.group(1); index_part = match.group(2)
        try:
            idx_val_str = evaluate_expression(index_part, variables, status_callback, True)
            idx_val = int(float(idx_val_str)) # Ensure index is integer
            f_name_int = f"{var_name.upper()}[{idx_val}]" # Use plain int index key
            # status_callback(f"DEBUG: Array Read Key: {f_name_int}") # Verbose Debug
            return variables.get(f_name_int, "0") # Default to "0" if key not found
        except Exception as e:
             if index_part.isdigit(): # Try direct integer if expression failed
                 idx_val = int(index_part)
                 f_name_int = f"{var_name.upper()}[{idx_val}]"
                 return variables.get(f_name_int, "0")
             if not is_sub_eval: status_callback(f"⚠️ Idx Err expr {var_name}[{index_part}]: {e}")
             return "0"
    # Add all known array bases
    sys_arrays = r"(\$P_SUBPAR|BP_OPT_QS3|BP_R_QS3|BP_AX_QS3|BP_RES_QS3|BP_OPTBIT_QS3)"
    processed_expr = re.sub(sys_arrays + r"\[(.*?)\]", replace_array_var_expr, processed_expr, flags=re.IGNORECASE)
    processed_expr = re.sub(r"(\b[A-Z]\w*)\[(.*?)\]", replace_array_var_expr, processed_expr) # General arrays

    # Simple variable substitution
    sys_simple = ["$P_SEARCH", "$P_SIM", "$P_DRYRUN", "MODE", "ERROR"] # Add known simple vars
    safe_vars = {k: v for k, v in variables.items() if isinstance(k, str)}
    vars_to_sub = list(safe_vars.items())
    for sv in sys_simple:
        if sv not in safe_vars: vars_to_sub.append((sv, "0")) # Default undefined system vars
    for var, val in sorted(vars_to_sub, key=lambda item: len(item[0]), reverse=True):
         pattern = r'\b{}\b'.format(re.escape(var)); flags = re.IGNORECASE if var.startswith('$') else 0
         processed_expr = re.sub(pattern, str(val), processed_expr, flags=flags)

    # Final evaluation using restricted eval()
    try:
        # Check if safe enough for eval (basic check)
        allowed = r"^[0-9\.\+\-\*\/\(\)\sEe&|^~]+$" # Added bitwise, exponent
        if not re.match(allowed, processed_expr):
             try: float(processed_expr); pass # Allow if just number like "1.23E-5"
             except ValueError: return processed_expr # Contains unsafe chars, return as string

        safe_globals={"__builtins__":None}; safe_locals={'math':math,'int':int,'float':float,'abs':abs,'round':round,'trunc':math.trunc}
        result = eval(processed_expr, safe_globals, safe_locals)
        return str(result)
    except Exception as e:
        # If eval failed, maybe it was just a number string?
        try: float(processed_expr); return processed_expr
        except ValueError: pass
        # Avoid logging errors during sub-evaluation unless needed
        if not is_sub_eval: status_callback(f"❌ Expr Eval Err: [{expr_str}]->[{processed_expr}]-> {e}")
        return processed_expr # Return processed string (might be desired literal)

# Keep _compare_values, evaluate_condition, bind_arguments, find_label_*
# (evaluate_condition updated below to include TRUNC in globals for eval base case)
def _compare_values(val1_str, val2_str, operator, variables, status_callback):
    eval_val1 = evaluate_expression(val1_str, variables, status_callback, True)
    eval_val2 = evaluate_expression(val2_str, variables, status_callback, True)
    num1, num2 = _try_numerical(eval_val1), _try_numerical(eval_val2)
    if isinstance(num1, float) and isinstance(num2, float):
        ops={'==':float.__eq__,'!=':float.__ne__,'<':float.__lt__,'>':float.__gt__,'<=':float.__le__,'>=':float.__ge__}
        return ops.get(operator, lambda a,b: False)(num1, num2)
    else: s1,s2 = str(eval_val1), str(eval_val2); return (s1==s2) if operator=='==' else (s1!=s2) if operator=='!=' else False



def evaluate_condition(condition_str, variables, status_callback):
    """Evaluates NC conditions, handling AND/OR, bitwise, arrays, and known system vars."""
    condition_str = condition_str.strip()

    # Bitwise replacements
    def int_wrap_bw(m):
        s = m.strip()
        ev = evaluate_expression(s, variables, status_callback, True)
        try:
            return str(int(float(ev)))
        except ValueError:
            status_callback(f"⚠️ BW op '{s}' → '{ev}' not numeric → 0.")
            return "0"

    # Replacing bitwise operations
    proc = re.sub(r'(\S+)\s+B_AND\s+(\S+)', lambda m: f"({int_wrap_bw(m.group(1))}&{int_wrap_bw(m.group(2))})", condition_str, flags=re.IGNORECASE)
    proc = re.sub(r'(\S+)\s+B_OR\s+(\S+)', lambda m: f"({int_wrap_bw(m.group(1))}|{int_wrap_bw(m.group(2))})", proc, flags=re.IGNORECASE)
    proc = re.sub(r'(\S+)\s+B_EXOR\s+(\S+)', lambda m: f"({int_wrap_bw(m.group(1))}^{int_wrap_bw(m.group(2))})", proc, flags=re.IGNORECASE)
    proc = re.sub(r'B_NOT\s+(\S+)', lambda m: f"(~{int_wrap_bw(m.group(1))})", proc, flags=re.IGNORECASE)

    # Handle nested OR/AND
    def split_top_level(expr, keyword):
        bal, parts, last = 0, [], 0
        i = 0
        while i < len(expr):
            if expr[i] == '(':
                bal += 1
            elif expr[i] == ')':
                bal -= 1
            elif bal == 0 and expr[i:i+len(keyword)].upper() == keyword:
                before = expr[i-1] if i > 0 else ''
                after = expr[i+len(keyword)] if i + len(keyword) < len(expr) else ''
                if not before.isalnum() and not after.isalnum():
                    parts.append(expr[last:i].strip())
                    last = i + len(keyword)
            i += 1
        if last > 0:
            parts.append(expr[last:].strip())
        return parts

    # Recurse OR first
    parts_or = split_top_level(proc, 'OR')
    if parts_or:
        for p in parts_or:
            if evaluate_condition(p, variables, status_callback):
                return True
        return False

    parts_and = split_top_level(proc, 'AND')
    if parts_and:
        for p in parts_and:
            if not evaluate_condition(p, variables, status_callback):
                return False
        return True

    # Array access replacements
    def repl_arr_cond(m):
        vn, ip = m.groups()
        vn = vn.upper()
        try:
            i_s = evaluate_expression(ip, variables, status_callback, True)
            i = int(float(i_s))
            return variables.get(f"{vn}[{i}]", "0")
        except:
            return variables.get(f"{vn}[{ip}]", "0")

    sys_arr = r"(\$P_SEARCH|\$P_SIM|\$P_DRYRUN|\$P_SUBPAR|BP_OPT_QS3|BP_R_QS3|BP_AX_QS3|BP_RES_QS3|BP_OPTBIT_QS3)"
    proc = re.sub(sys_arr + r"\[(.*?)\]", repl_arr_cond, proc, flags=re.IGNORECASE)
    proc = re.sub(r"(\b[A-Z]\w*)\[(.*?)\]", repl_arr_cond, proc)  # Generic arrays

    # Ensure system variables are defined
    sys_vars = ["$P_SEARCH", "$P_SIM", "$P_DRYRUN", "$P_SUBPAR"]
    for sv in sys_vars:
        if sv not in variables:
            variables[sv] = "0"  # Default to 0 if undefined

    # Basic variable substitution
    for var, val in sorted(variables.items(), key=lambda i: len(i[0]), reverse=True):
        if not isinstance(var, str):
            continue
        pat = r'\b{}\b'.format(re.escape(var))
        flags = re.IGNORECASE if var.startswith('$') else 0
        proc = re.sub(pat, str(val), proc, flags=flags)

    # Replace logical/boolean syntax
    proc = re.sub(r'\bFALSE\b', '0', proc, flags=re.IGNORECASE)
    proc = re.sub(r'\bTRUE\b', '1', proc, flags=re.IGNORECASE)
    proc = re.sub(r'\bNOT\b', ' not ', proc, flags=re.IGNORECASE)
    proc = proc.replace("<>", "!=").replace("===", "==").replace("=>", ">=")

    # Debug the transformation
    # status_callback(f"🧪 Eval Attempt: {condition_str} → {proc}")

    try:
        # Try comparison-based match
        m_comp = re.match(r"^\s*(.*?)\s*(==|!=|>|<|>=|<=)\s*(.*?)\s*$", proc)
        if m_comp:
            op1, oper, op2 = m_comp.groups()
            return bool(_compare_values(op1.strip(), op2.strip(), oper, variables, status_callback))

        # Reject unsafe strings (not math)
        if not re.match(r'^[\d\.\+\-\*/\(\)\s]+$', proc):
            status_callback(f"❌ Unsafe expression fallback blocked: {proc}")
            return False

        # Safe fallback evaluation
        safe_globals = {
            "__builtins__": None,
            "int": int, "float": float, "abs": abs,
            "round": round, "bool": bool, "True": True, "False": False,
            "trunc": math.trunc
        }
        eval_r = eval(proc, safe_globals, {})
        result = bool(_try_numerical(eval_r)) if isinstance(eval_r, (float, int)) else bool(eval_r)
        return result

    except Exception as e:
        status_callback(f"❌ Final Eval Exception: [{condition_str}] → [{proc}] → {e}")
        return False









"# --- End of File ---"