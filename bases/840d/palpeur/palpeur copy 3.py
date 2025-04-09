
# -*- coding: utf-8 -*- # Added encoding declaration
import os
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import math

# --- Constants ---
BASE_PATH = "nc_programs"
DEFAULT_CALL = "BP9725(0,,10,,,-20,,,22,,,0,,,-1)" # Example BP9725 call

# --- Helper Functions ---

def parse_call(call_str):
    """Parses BPxxxx(...) calls, returning func_name, args_list, error_msg."""
    match = re.match(r"(BP\d+)\s*\((.*)\)", call_str.strip())
    if not match:
        return None, None, f"Invalid format. Use: BPxxxx(...)"
    func = match.group(1).upper()
    args_str = match.group(2).strip()
    if not args_str:
        args = []
    else:
        args_raw = [a.strip() for a in args_str.split(',')]
        args = [arg if arg else None for arg in args_raw]
    return func, args, None

def read_file(name, status_callback):
    """Reads NC program file, trying different encodings."""
    path = os.path.join(BASE_PATH, f"{name}.nc")
    if not os.path.isfile(path):
        status_callback(f"❌ File not found: {path}")
        return None
    encodings_to_try = ['utf-8', 'iso-8859-1', 'cp1252', 'latin-1']
    content = None
    last_error = None
    for enc in encodings_to_try:
        try:
            with open(path, 'r', encoding=enc) as f: content = f.readlines()
            status_callback(f"📂 Loaded: {path} (Encoding: {enc})")
            return content
        except UnicodeDecodeError as e: last_error = e; continue
        except Exception as e: status_callback(f"❌ Error reading {path}: {e}"); return None
    status_callback(f"❌ Failed to decode {path}. Last error: {last_error}")
    return None

def extract_movements(code_line):
    """Extracts G-code movement commands and coordinates."""
    movements = re.findall(r'\bG([0-3])\b', code_line)
    movements.extend(re.findall(r'\bG(4)\b', code_line))
    descriptions = {'G0': 'Rapid', 'G1': 'Linear', 'G2': 'CW Arc', 'G3': 'CCW Arc', 'G4': 'Dwell'}
    coords = re.findall(r'([XYZABCUVW])([-+]?\d*\.?\d+)', code_line, re.IGNORECASE)
    coord_str = " ".join([f"{ax}{val}" for ax, val in coords])
    results = [f"G{m_code} ({descriptions.get(f'G{m_code}', 'Unknown G')}) {coord_str}".strip() for m_code in movements]
    return results

def extract_condition(line):
    """Extracts the condition part from IF(...) GOTOx statements."""
    # Improved regex to handle simple nesting, might still fail on complex cases
    # Assumes GOTOx follows the condition's closing parenthesis
    match = re.search(r"IF\s*\((.*)\)\s*(?:GOTOF|GOTO|THEN)", line, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None

def _try_numerical(val_str):
    """Attempt conversion to float, return original string if failed."""
    if val_str is None: return None
    try: return float(val_str)
    except (ValueError, TypeError): return str(val_str)

def _compare_values(val1_str, val2_str, operator, variables, status_callback):
    """Compares two STRINGS, evaluating them first if complex."""
    eval_val1 = evaluate_expression(val1_str, variables, status_callback, is_sub_eval=True)
    eval_val2 = evaluate_expression(val2_str, variables, status_callback, is_sub_eval=True)
    num1 = _try_numerical(eval_val1)
    num2 = _try_numerical(eval_val2)
    if isinstance(num1, float) and isinstance(num2, float):
        ops = {'==': float.__eq__, '!=': float.__ne__, '<': float.__lt__, '>': float.__gt__, '<=': float.__le__, '>=': float.__ge__}
        return ops.get(operator, lambda a, b: False)(num1, num2)
    else:
        s1, s2 = str(eval_val1), str(eval_val2)
        if operator == '==': return s1 == s2
        if operator == '!=': return s1 != s2
        return False
    return False

def evaluate_expression(expr_str, variables, status_callback, is_sub_eval=False):
    """Evaluates NC expressions with substitutions and basic math."""
    # (Keep the robust evaluate_expression function from the previous full script)
    # ... (it handles functions, array vars, simple vars, and basic math via eval) ...
    if expr_str is None: return "0"
    processed_expr = str(expr_str).strip()
    # Function handling (ABS, ROUND, SQRT, SIN, COS)
    def handle_func(match):
         func_name = match.group(1).upper(); func_arg_str = match.group(2)
         arg_val_str = evaluate_expression(func_arg_str, variables, status_callback, True)
         try:
              arg_val_num = float(arg_val_str)
              if func_name == 'ABS': return str(abs(arg_val_num))
              if func_name == 'ROUND': return str(round(arg_val_num))
              if func_name == 'SQRT': return str(math.sqrt(arg_val_num))
              if func_name == 'SIN': return str(math.sin(math.radians(arg_val_num)))
              if func_name == 'COS': return str(math.cos(math.radians(arg_val_num)))
              else: return match.group(0)
         except Exception as e:
              if not is_sub_eval: status_callback(f"⚠️ Func Error {func_name}({arg_val_str}): {e}")
              return match.group(0)
    processed_expr = re.sub(r"\b(ABS|ROUND|SQRT|SIN|COS)\s*\(\s*(.*?)\s*\)", handle_func, processed_expr, flags=re.IGNORECASE)
    # Array variable substitution
    def replace_array_var_expr(match):
        var_name = match.group(1); index_part = match.group(2)
        try:
            idx_val_str = evaluate_expression(index_part, variables, status_callback, True)
            idx_val = int(float(idx_val_str))
            f_name = f"{var_name.upper()}[{idx_val}]"
            return variables.get(f_name, "0")
        except Exception:
             if index_part.isdigit():
                  f_name = f"{var_name.upper()}[{int(index_part)}]"
                  return variables.get(f_name, "0")
             if not is_sub_eval: status_callback(f"⚠️ Idx Error expr {var_name}[{index_part}]")
             return "0"
    processed_expr = re.sub(r"(\$P_SEARCH|\$P_SIM|\$P_DRYRUN|\$P_SUBPAR)\[(.*?)\]", replace_array_var_expr, processed_expr, flags=re.IGNORECASE)
    processed_expr = re.sub(r"(\b\w+)\[(.*?)\]", replace_array_var_expr, processed_expr)
    # Simple variable substitution
    safe_vars = {k: v for k, v in variables.items() if isinstance(k, str)}
    for var, val in sorted(safe_vars.items(), key=lambda item: len(item[0]), reverse=True):
         pattern = r'\b{}\b'.format(re.escape(var)); flags = re.IGNORECASE if var.startswith('$') else 0
         processed_expr = re.sub(pattern, str(val), processed_expr, flags=flags)
    # Final evaluation
    try:
        safe_globals = {"__builtins__": None}; safe_locals = {'math': math}
        result = eval(processed_expr, safe_globals, safe_locals)
        return str(result)
    except Exception as e:
        if not any(op in processed_expr for op in ['+', '-', '*', '/', '(', ')']): return processed_expr # Likely literal
        if not is_sub_eval: status_callback(f"❌ Expr Eval Error: [{expr_str}]->[{processed_expr}]-> {e}")
        return expr_str # Return original on error

# --- THIS IS THE NEWLY ADDED FUNCTION ---
def update_variables(line, variables, status_callback):
    """Processes an assignment line VAR = expression."""
    match = re.match(r"\s*([\w$]+(?:\[.*?\])?)\s*=\s*(.*)", line.strip(), re.IGNORECASE)
    if match:
        var_name = match.group(1).upper()
        expr_str = match.group(2).strip()
        value = evaluate_expression(expr_str, variables, status_callback)
        variables[var_name] = str(value) # Store as string
        # status_callback(f" Assignment: {var_name} = {value} (from '{expr_str}')") # Logged by evaluate_expression now
    return variables
# --- END OF NEWLY ADDED FUNCTION ---

# --- REVISED evaluate_condition to handle basic AND/OR ---
def evaluate_condition(condition_str, variables, status_callback):
    """Evaluates NC conditions, handling basic AND/OR."""
    condition_str = condition_str.strip()
    # Handle outer parentheses
    if condition_str.startswith('(') and condition_str.endswith(')'):
        balance = 0; match = True
        for i, char in enumerate(condition_str):
            if char == '(': balance += 1
            elif char == ')': balance -= 1
            if balance == 0 and i < len(condition_str) - 1: match = False; break
        if match and balance == 0:
             return evaluate_condition(condition_str[1:-1], variables, status_callback)

    # Split by OR (lowest precedence) at top level
    balance = 0; split_indices = []
    for i, char in enumerate(condition_str):
        if char == '(': balance += 1
        elif char == ')': balance -= 1
        elif balance == 0 and condition_str[i:i+2].upper() == 'OR':
            # Check if it's a whole word 'OR'
            prev_char_ok = i == 0 or not condition_str[i-1].isalnum()
            next_char_ok = i + 2 == len(condition_str) or not condition_str[i+2].isalnum()
            if prev_char_ok and next_char_ok:
                 split_indices.append(i)

    if split_indices:
        parts = []; last_idx = 0
        for idx in split_indices: parts.append(condition_str[last_idx:idx].strip()); last_idx = idx + 2
        parts.append(condition_str[last_idx:].strip())
        for part in parts:
            if evaluate_condition(part, variables, status_callback):
                # status_callback(f"🧠 OR group [{condition_str}] -> True (due to '{part}')")
                return True
        # status_callback(f"🧠 OR group [{condition_str}] -> False")
        return False

    # Split by AND (higher precedence) at top level
    balance = 0; split_indices = []
    for i, char in enumerate(condition_str):
        if char == '(': balance += 1
        elif char == ')': balance -= 1
        elif balance == 0 and condition_str[i:i+3].upper() == 'AND':
            prev_char_ok = i == 0 or not condition_str[i-1].isalnum()
            next_char_ok = i + 3 == len(condition_str) or not condition_str[i+3].isalnum()
            if prev_char_ok and next_char_ok:
                split_indices.append(i)

    if split_indices:
        parts = []; last_idx = 0
        for idx in split_indices: parts.append(condition_str[last_idx:idx].strip()); last_idx = idx + 3
        parts.append(condition_str[last_idx:].strip())
        for part in parts:
            if not evaluate_condition(part, variables, status_callback):
                # status_callback(f"🧠 AND group [{condition_str}] -> False (due to '{part}')")
                return False
        # status_callback(f"🧠 AND group [{condition_str}] -> True")
        return True

    # Base Case: Simple Comparison or Single Value
    processed_condition = condition_str
    # Substitute arrays and variables
    def replace_array_var_cond(match):
        var_name, index_part = match.groups()
        try:
            idx_val_str = evaluate_expression(index_part, variables, status_callback, True)
            idx_val = int(float(idx_val_str)); f_name = f"{var_name.upper()}[{idx_val}]"
            return variables.get(f_name, "False") # Default to False for missing condition vars
        except Exception:
             if index_part.isdigit(): f_name = f"{var_name.upper()}[{int(index_part)}]"; return variables.get(f_name, "False")
             return "False"
    sys_vars = r"(\$P_SEARCH|\$P_SIM|\$P_DRYRUN|\$P_SUBPAR)" # Add more system vars if needed
    processed_condition = re.sub(sys_vars + r"\[(.*?)\]", replace_array_var_cond, processed_condition, flags=re.IGNORECASE)
    processed_condition = re.sub(r"(\b\w+)\[(.*?)\]", replace_array_var_cond, processed_condition) # General arrays

    safe_vars = {k: v for k, v in variables.items() if isinstance(k, str)}
    for var, val in sorted(safe_vars.items(), key=lambda item: len(item[0]), reverse=True):
         pattern = r'\b{}\b'.format(re.escape(var)); flags = re.IGNORECASE if var.startswith('$') else 0
         processed_condition = re.sub(pattern, str(val), processed_condition, flags=flags)

    processed_condition = re.sub(r'\bTRUE\b', '1', processed_condition, flags=re.IGNORECASE)
    processed_condition = re.sub(r'\bFALSE\b', '0', processed_condition, flags=re.IGNORECASE)
    processed_condition = processed_condition.replace("<>", "!=").replace("=", "==").replace("===", "==").replace("=>", ">=")

    try:
        match_comp = re.match(r"^\s*(.*?)\s*(==|!=|>|<|>=|<=)\s*(.*?)\s*$", processed_condition)
        if match_comp:
            op1_str, operator, op2_str = match_comp.groups()
            result = _compare_values(op1_str.strip(), op2_str.strip(), operator, variables, status_callback)
            status_callback(f"🧠 Cmp: [{condition_str}] -> Compare ('{op1_str}' {operator} '{op2_str}') -> {result}")
            return bool(result)
        else:
             eval_val = evaluate_expression(processed_condition, variables, status_callback, is_sub_eval=True)
             num_val = _try_numerical(eval_val)
             if isinstance(num_val, float): result = (num_val != 0.0)
             else: result = bool(eval_val) and eval_val.upper() != 'FALSE' # Treat only 0/empty/'FALSE' as False
             status_callback(f"🧠 Bool: [{condition_str}] -> Eval ('{eval_val}') -> {result}")
             return result
    except Exception as e:
        status_callback(f"❌ Base Cond Error: [{condition_str}] -> [{processed_condition}] -> {e}")
        return False
# --- END REVISED evaluate_condition ---


def bind_arguments(args_list, target_vars, status_callback, is_subcall=False):
    """Binds passed arguments list to BP_x, $P_SUBPAR[x] in target_vars."""
    # (Keep function from previous full script)
    if args_list is None: return target_vars
    for i, arg_val in enumerate(args_list):
        bp_name = f"BP_{i + 1}"; subpar_name = f"$P_SUBPAR[{i + 1}]"
        if arg_val is not None:
            target_vars[bp_name] = str(arg_val); target_vars[subpar_name] = "True"
        else: target_vars[bp_name] = "0"; target_vars[subpar_name] = "False"
    return target_vars

def find_label_forward(content, label, start_index, status_callback):
    """Searches for label forward from start_index + 1."""
    # (Keep function from previous full script)
    label_pattern = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for idx in range(start_index + 1, len(content)):
        if label_pattern.match(content[idx].strip()): return idx
    status_callback(f"⚠️ Label {label} not found Forward from L{start_index + 2}.")
    return len(content)

def find_label_backward(content, label, start_index, status_callback):
    """Searches for label backward from start_index - 1."""
    # (Keep function from previous full script)
    label_pattern = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for idx in range(start_index - 1, -1, -1):
        if label_pattern.match(content[idx].strip()): return idx
    status_callback(f"⚠️ Label {label} not found Backward from L{start_index}.")
    return len(content)

def find_label_any(content, label, status_callback):
    """Default GOTO search (forward from start)."""
    # (Keep function from previous full script)
    label_pattern = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for idx, line in enumerate(content):
        if label_pattern.match(line.strip()): return idx
    status_callback(f"⚠️ Label {label} not found in program.")
    return len(content)


# --- Tkinter GUI Class ---
class NC_Debugger_GUI:
    # (Keep __init__ from previous full script)
    def __init__(self, master):
        self.master = master
        master.title("NC Code Debugger")
        master.geometry("1000x800") # Adjusted size
        self.mono_font = font.Font(family="Courier New", size=10)
        self.status_font = font.Font(family="Segoe UI", size=9)
        self.program_content = []
        self.current_line_index = 0
        self.variables = {}
        self.movements = []
        self.current_func_name = ""
        self.simulation_active = False
        self.call_stack = []
        # --- GUI Layout (Keep from previous full script) ---
        top_frame = tk.Frame(master, pady=5); top_frame.pack(fill=tk.X, padx=5)
        tk.Label(top_frame, text="Call:").pack(side=tk.LEFT)
        self.call_entry = tk.Entry(top_frame, width=60); self.call_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True); self.call_entry.insert(0, DEFAULT_CALL)
        self.load_button = tk.Button(top_frame, text="Load", command=self.load_program, width=8); self.load_button.pack(side=tk.LEFT, padx=2)
        self.step_button = tk.Button(top_frame, text="Step", command=self.step_execution, state=tk.DISABLED, width=8); self.step_button.pack(side=tk.LEFT, padx=2)
        self.reset_button = tk.Button(top_frame, text="Reset", command=self.reset_simulation, state=tk.DISABLED, width=8); self.reset_button.pack(side=tk.LEFT, padx=2)
        main_pane = tk.PanedWindow(master, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bd=2); main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        code_frame = tk.LabelFrame(main_pane, text="Program Code", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.NONE, font=self.mono_font, height=20, width=80); self.code_text.pack(fill=tk.BOTH, expand=True); self.code_text.tag_configure("highlight", background="yellow", borderwidth=1, relief=tk.RAISED); self.code_text.config(state=tk.DISABLED)
        main_pane.add(code_frame, stretch="always")
        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, sashrelief=tk.RAISED, bd=2); main_pane.add(right_pane, stretch="never", width=350)
        stack_frame = tk.LabelFrame(right_pane, text="Call Stack", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.stack_text = scrolledtext.ScrolledText(stack_frame, wrap=tk.NONE, font=self.mono_font, height=6, width=45); self.stack_text.pack(fill=tk.BOTH, expand=True); self.stack_text.config(state=tk.DISABLED)
        right_pane.add(stack_frame, stretch="never", height=120)
        var_frame = tk.LabelFrame(right_pane, text="Variables", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.var_text = scrolledtext.ScrolledText(var_frame, wrap=tk.NONE, font=self.mono_font, height=15, width=45); self.var_text.pack(fill=tk.BOTH, expand=True); self.var_text.config(state=tk.DISABLED)
        right_pane.add(var_frame, stretch="always")
        move_frame = tk.LabelFrame(right_pane, text="Movement Log", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.move_text = scrolledtext.ScrolledText(move_frame, wrap=tk.NONE, font=self.mono_font, height=10, width=45); self.move_text.pack(fill=tk.BOTH, expand=True); self.move_text.config(state=tk.DISABLED)
        right_pane.add(move_frame, stretch="always")
        self.status_label = tk.Label(master, text="Status: Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.status_font); self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)


    # --- GUI Methods ---
    # (Keep update_status, update_code_display, update_call_stack_display, load_program, etc.)
    # ... from previous full script ...
    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        print(f"DEBUG: {message}") # Console log
        self.master.update_idletasks()

    def update_code_display(self):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete('1.0', tk.END)
        parent = self.code_text.master
        title = f"Code: {self.current_func_name}.nc" if self.current_func_name else "Program Code"
        if isinstance(parent, tk.LabelFrame): parent.config(text=title)
        if self.program_content:
            for i, line in enumerate(self.program_content): self.code_text.insert(tk.END, f"{i+1:04d}: {line}")
        self.code_text.config(state=tk.DISABLED)
        self.highlight_line()

    def update_call_stack_display(self):
        self.stack_text.config(state=tk.NORMAL); self.stack_text.delete('1.0', tk.END)
        if not self.call_stack: self.stack_text.insert('1.0', "(Stack Empty)")
        else:
            for i, (fname, _, ret_idx, _) in reversed(list(enumerate(self.call_stack))):
                self.stack_text.insert('1.0', f"{i}: {fname} (ret L{ret_idx + 1})\n")
        self.stack_text.config(state=tk.DISABLED)

    def load_program(self):
        self.reset_simulation(clear_call=False)
        call_str = self.call_entry.get()
        if not call_str: messagebox.showerror("Error", "Enter function call."); return
        func_name, args, error_msg = parse_call(call_str)
        if error_msg: messagebox.showerror("Error", error_msg); return
        self.update_status(f"Loading: {func_name}")
        content = read_file(func_name, self.update_status)
        if content:
            self.program_content = content; self.current_func_name = func_name
            self.variables = bind_arguments(args, {}, self.update_status, False)
            self.current_line_index = 0; self.simulation_active = True
            self.update_displays()
            self.step_button.config(state=tk.NORMAL); self.reset_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.DISABLED)
            self.update_status(f"Loaded {func_name}. Ready.")
        else: messagebox.showerror("Error", f"Load failed: {func_name}."); self.reset_simulation()

    def step_execution(self):
        # (Keep the step_execution logic that calls the handle_... methods)
        if not self.simulation_active: self.update_status("Simulation inactive."); return
        if self.current_line_index >= len(self.program_content): self.end_of_program_check(); return

        line_num = self.current_line_index
        line = self.program_content[line_num].strip()
        upper_line = line.upper()

        self.highlight_line()
        self.update_status(f"Exec L{line_num + 1} ({self.current_func_name}): {line[:80]}") # Limit line length in status

        next_line_index = self.current_line_index + 1
        jumped, call_occurred, return_occurred = False, False, False

        # Execution Logic (Ordered)
        if not line or line.startswith(';') or line.startswith('%'): pass
        elif "M17" in upper_line: return_occurred = self.handle_return(is_m17=True)
        elif "M30" in upper_line: self.handle_m30(); return
        elif re.match(r"^\s*(BP\d+)\s*\(", line, re.IGNORECASE): call_occurred = self.handle_subprogram_call(line)
        elif upper_line.startswith("IF"): next_line_index, jumped = self.handle_conditional_jump(line, upper_line, line_num)
        elif upper_line.startswith("GOTOF"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "F")
        elif upper_line.startswith("GOTOB"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "B")
        elif upper_line.startswith("GOTO"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "A")
        elif "=" in line and not upper_line.startswith("IF"): self.handle_assignment(line) # Use handle_ method
        elif re.search(r'\bG[0-9]+\b', line): self.handle_movement(line, line_num)
        elif re.match(r"^\s*LBL\d+\s*:", line, re.IGNORECASE): pass # Label def
        # Handle DEF statements (skip them)
        elif upper_line.startswith("DEF"): self.update_status(f"  Skipping DEF: {line}")
        else: self.update_status(f"  Skipping unrecognized: {line}")

        # Update state
        if not call_occurred and not return_occurred and self.simulation_active:
             self.current_line_index = next_line_index
             if self.current_line_index >= len(self.program_content): self.end_of_program_check()

    def handle_m30(self):
        # (Keep from previous full script)
        self.update_status("🏁 M30: Program End reached."); self.simulation_active = False
        self.step_button.config(state=tk.DISABLED); self.call_stack = []; self.update_call_stack_display()

    def handle_subprogram_call(self, line):
        # (Keep from previous full script)
        call_match = re.match(r"^\s*(BP\d+)\s*\((.*)\)", line, re.IGNORECASE)
        if not call_match: self.update_status(f"⚠️ Sub Call Parse Fail: {line}"); return False
        sub_func, sub_args_str = call_match.groups(); sub_func = sub_func.upper()
        _, sub_args_list, parse_err = parse_call(f"{sub_func}({sub_args_str})")
        if parse_err: self.update_status(f"❌ Sub Arg Parse Error: {parse_err}"); return False
        sub_content = read_file(sub_func, self.update_status)
        if sub_content:
            ret_idx = self.current_line_index + 1
            self.call_stack.append((self.current_func_name, self.program_content, ret_idx, self.variables.copy()))
            self.update_call_stack_display()
            self.current_func_name = sub_func; self.program_content = sub_content; self.current_line_index = 0
            self.variables = bind_arguments(sub_args_list, {}, self.update_status, True)
            self.update_displays(); return True
        else: self.update_status(f"⚠️ Sub File Load Fail: {sub_func}. Skipping."); return False

    def handle_conditional_jump(self, line, upper_line, line_num):
        # (Keep from previous full script)
        condition_str = extract_condition(line); next_idx = line_num + 1; jumped = False
        jump_match = re.search(r"\)\s*(GOTOF|GOTO)\s+(LBL\d+)", upper_line, re.IGNORECASE)
        if condition_str and jump_match:
            jump_type, dest = jump_match.groups()
            result = evaluate_condition(condition_str, self.variables, self.update_status)
            take_jump = (jump_type == "GOTOF" and not result) or (jump_type == "GOTO" and result)
            if take_jump:
                target_idx = find_label_forward(self.program_content, dest, line_num, self.update_status)
                next_idx = target_idx; jumped = True
                # Status logged by evaluate_condition
            # else: self.update_status(f" IF condition not met.") # Optional status
        else: self.update_status(f"⚠️ Malformed IF: {line}")
        return next_idx, jumped

    def handle_unconditional_jump(self, upper_line, line_num, jump_mode):
        # (Keep from previous full script)
        jump_type = "GOTO" + (jump_mode if jump_mode != "A" else ""); next_idx = line_num + 1; jumped = False
        dest_match = re.match(rf"{jump_type}\s+(LBL\d+)", upper_line, re.IGNORECASE)
        if dest_match:
            dest = dest_match.group(1)
            if jump_mode == "F": target_idx = find_label_forward(self.program_content, dest, line_num, self.update_status)
            elif jump_mode == "B": target_idx = find_label_backward(self.program_content, dest, line_num, self.update_status)
            else: target_idx = find_label_forward(self.program_content, dest, line_num, self.update_status)
            next_idx = target_idx; jumped = True
            self.update_status(f" Uncond {jump_type} to {dest} (L{target_idx+1})")
        else: self.update_status(f"⚠️ Malformed {jump_type}: {upper_line}")
        return next_idx, jumped

    # THIS METHOD NOW CALLS THE GLOBAL update_variables FUNCTION
    def handle_assignment(self, line):
        """Handles variable assignment by calling the helper function."""
        self.variables = update_variables(line, self.variables, self.update_status)
        self.update_variable_display()

    def handle_movement(self, line, line_num):
        # (Keep from previous full script)
        move_info = extract_movements(line)
        if move_info:
            log_prefix = f"L{line_num+1} ({self.current_func_name}):"
            for move in move_info: self.movements.append(f"{log_prefix} {move}")
            self.update_movement_log()

    def handle_return(self, is_m17):
        # (Keep from previous full script)
        if self.call_stack:
            c_func, c_cont, c_ret_idx, c_vars = self.call_stack.pop(); self.update_call_stack_display()
            self.current_func_name = c_func; self.program_content = c_cont; self.current_line_index = c_ret_idx
            self.variables = c_vars; self.update_displays()
            self.update_status(f"↩️ Returned to {c_func} at L{c_ret_idx + 1}"); return True
        else:
            status = "⚠️ M17 at base level." if is_m17 else "🏁 End of file at base."
            self.update_status(status + " Stopping."); self.simulation_active = False
            self.step_button.config(state=tk.DISABLED); return False

    def end_of_program_check(self):
        # (Keep from previous full script)
        # self.update_status("🏁 Reached end of file.") # Called handle_return now
        if self.call_stack: self.handle_return(is_m17=False)
        else: self.simulation_active = False; self.step_button.config(state=tk.DISABLED)

    def update_displays(self):
        # (Keep from previous full script)
        self.update_code_display(); self.update_variable_display();
        self.update_movement_log(); self.update_call_stack_display()

    def update_variable_display(self):
        # (Keep from previous full script)
        self.var_text.config(state=tk.NORMAL); self.var_text.delete('1.0', tk.END)
        if self.variables:
            for k, v in sorted(self.variables.items()): self.var_text.insert(tk.END, f"{k} = {v}\n")
        else: self.var_text.insert('1.0', "(No variables)")
        self.var_text.config(state=tk.DISABLED); self.var_text.yview_moveto(0)

    def update_movement_log(self):
        # (Keep from previous full script)
        self.move_text.config(state=tk.NORMAL); self.move_text.delete('1.0', tk.END)
        if self.movements:
            for move in self.movements: self.move_text.insert(tk.END, f"{move}\n")
        else: self.move_text.insert('1.0', "(No movements logged)")
        self.move_text.config(state=tk.DISABLED); self.move_text.see(tk.END)

    def highlight_line(self):
        # (Keep from previous full script)
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        if not self.program_content or self.current_line_index >= len(self.program_content): return
        line_start = f"{self.current_line_index + 1}.0"; line_end = f"{self.current_line_index + 1}.end"
        tag_start = f"{self.current_line_index + 1}.6"
        try: self.code_text.tag_add("highlight", tag_start, line_end); self.code_text.see(line_start)
        except tk.TclError: self.update_status(f"⚠️ Error highlighting L{self.current_line_index + 1}")

    def reset_simulation(self, clear_call=True):
        # (Keep from previous full script)
        self.program_content = []; self.current_line_index = 0; self.variables = {}
        self.movements = []; self.current_func_name = ""; self.simulation_active = False
        self.call_stack = []
        # Clear displays
        self.update_displays()
        for widget in [self.code_text, self.var_text, self.move_text, self.stack_text]:
             widget.config(state=tk.NORMAL); widget.delete('1.0', tk.END); widget.config(state=tk.DISABLED)
        parent = self.code_text.master
        if isinstance(parent, tk.LabelFrame): parent.config(text="Program Code")
        self.var_text.config(state=tk.NORMAL); self.var_text.insert('1.0', "(No variables)"); self.var_text.config(state=tk.DISABLED)
        self.move_text.config(state=tk.NORMAL); self.move_text.insert('1.0', "(No movements)"); self.move_text.config(state=tk.DISABLED)
        self.stack_text.config(state=tk.NORMAL); self.stack_text.insert('1.0', "(Stack Empty)"); self.stack_text.config(state=tk.DISABLED)
        if clear_call: self.call_entry.delete(0, tk.END)
        self.step_button.config(state=tk.DISABLED); self.reset_button.config(state=tk.DISABLED); self.load_button.config(state=tk.NORMAL)
        self.update_status("Ready. Enter function call and press Load.")


# --- Main Execution ---
if __name__ == "__main__":
    # (Keep the main block that creates the directory, dummy files, and runs the GUI)
    if not os.path.exists(BASE_PATH):
        try:
            os.makedirs(BASE_PATH)
            print(f"Created directory: {BASE_PATH}")
            dummy_files = {
                "BP9725.nc": """
;QUICKSTART V3AC CB COPYRIGHT BLUM-NOVOTEST GMBH 01.07.2015
;OPTION P03.8000-031.305.102

DEF INT BP_10, BP_METRINCH, BP_COUNTER, BP_OPTBIT_MEASURE, BP_OPTBIT_SETTINGS
IF (($P_SEARCH) OR ($P_SIM) OR ($P_DRYRUN)) GOTOF LBL_SIM ; Test OR

LBL200: IF($P_SUBPAR[1]<>FALSE)GOTOF LBL201 ; Test SUBPAR access
BP_1=9999 ; Default if not passed

LBL201:
; Use passed args if available
IF ($P_SUBPAR[1] == TRUE) THEN BP_10 = BP_1 ; Example THEN usage (not fully supported yet)
G0 X=BP_1 Y=BP_3 ; Use args (BP_3 might be default 0)
MYVAR = 100
IF (BP_2 <> 0) GOTOF LBL5 ; Jump if BP_2 is NOT 0 (passed as 0, so should NOT jump)
G1 Z-5 F100
MYVAR = MYVAR + 5
GOTO LBL_SKIP_ADD ; Plain GOTO

LBL5:
G1 X50 Y50 ; Should execute if BP_2 was 0
MYVAR = MYVAR + 10

LBL_SKIP_ADD:
BP9710(MYVAR, BP_2 + 1) ; Call subprogram with calculated arg

G0 Z100
GOTOB LBL5 ; Jump backward

LBL_SIM:
; Simulation-only path
MVAR = 1
IF (MVAR == 1 AND $P_SIM == TRUE) GOTO LBL_END_SIM ; Test AND

LBL_END_SIM:
M30
""",
                "BP9710.nc": """
N10 ; Subprogram BP9710 called with MYVAR, BP_2+1
N20 DEF REAL SUBVAR
N30 SUBVAR = BP_1 * 2 ; BP_1 is MYVAR from caller
N40 G1 X=SUBVAR Y=BP_2 F500 ; Use BP_2 (caller's BP_2+1)
N50 IF (SUBVAR > 210) GOTO LBL_SUB_END
N60 G0 Z10
N70 LBL_SUB_END:
N80 M17 ; Return
"""
            }
            for filename, content in dummy_files.items():
                filepath = os.path.join(BASE_PATH, filename)
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding='utf-8') as f: f.write(content.strip())
                    print(f"Created dummy file: {filepath}")
        except Exception as e: print(f"Error creating base path/dummy files: {e}")

    root = tk.Tk()
    gui = NC_Debugger_GUI(root)
    root.mainloop()
