'''
This version will provide:

1.  **Code View:** Display the loaded NC program with the current execution line highlighted.
2.  **Controls:** Buttons to Load, Step through the code, and Reset.
3.  **Variable View:** Show the current state of variables (`BP_x`, `$P_SUBPAR`, etc.).
4.  **Movement Log:** List the G-code movements encountered during execution.
5.  **Input:** An entry field for the initial function call.
6.  **Status Bar:** Display messages about the simulation process.
'''

import os
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, font

# --- Constants and Original Helper Functions (slightly adapted) ---

subprograms_called = set() # Reset on each load
BASE_PATH = "nc_programs" # Make sure this directory exists and contains your .nc files
DEFAULT_CALL = "BP9725(0,,10,,,-20,,,22,,,0,,,-1)"
# PARAM_FILE = "parameters.txt" # Parameter persistence is less direct in GUI, removed for simplicity

# Parse the call like BP9725(0,,10,,,-20...)
def parse_call(call_str):
    match = re.match(r"(BP\d+)\((.*)\)", call_str)
    if not match:
        return None, []
    func = match.group(1)
    # Handle potential trailing comma or empty string after split
    args_raw = match.group(2).split(',')
    args = [arg.strip() if arg.strip() else None for arg in args_raw]
    # If the last character was a comma, split might add an extra empty element
    if match.group(2).endswith(',') and args[-1] is None:
         # We can potentially keep it or remove it depending on desired behavior.
         # Let's assume trailing commas might imply a final None argument.
         pass # Keep the potential trailing None
    # Filter out purely empty strings if they are not meaningful Nones
    # args = [a for a in args if a is not None or isinstance(a, str)] # Example refinement if needed
    return func, args

# Read file contents
def read_file(name, status_callback):
    path = os.path.join(BASE_PATH, f"{name}.nc")
    if os.path.isfile(path):
        try:
            with open(path, 'r') as f:
                status_callback(f"📂 Loaded: {path}")
                return f.readlines()
        except Exception as e:
            status_callback(f"❌ Error reading file {path}: {e}")
            return None
    else:
        status_callback(f"❌ File not found: {path}")
        return None

# Parameter persistence (optional memory) - Kept if needed, but less integrated here
# def load_parameters():
#     parameters = {}
#     if os.path.exists(PARAM_FILE):
#         with open(PARAM_FILE, 'r') as f:
#             for line in f:
#                 key, value = line.strip().split('=')
#                 parameters[key] = value
#     return parameters

# def save_parameters(parameters):
#     with open(PARAM_FILE, 'w') as f:
#         for key, value in parameters.items():
#             f.write(f"{key}={value}\n")

# Detect G-code movements
def extract_movements(code_line):
    # More specific regex to avoid capturing things like GOTO
    movements = re.findall(r'\bG([0-3])\b', code_line) # G0, G1, G2, G3
    movements.extend(re.findall(r'\bG(4)\b', code_line)) # G4 (Dwell)
    # Add more specific G-codes if needed, e.g., G90, G91 etc. if they imply movement state
    # movements.extend(re.findall(r'\b(G90|G91)\b', code_line))

    descriptions = {
        'G0': 'Rapid movement (non-cutting)',
        'G1': 'Linear movement',
        'G2': 'Circular CW',
        'G3': 'Circular CCW',
        'G4': 'Dwell (pause)',
        # 'G90': 'Absolute programming',
        # 'G91': 'Incremental programming',
    }
    # Extract axis values for context
    coords = re.findall(r'([XYZABCUVW])([-+]?\d*\.?\d+)', code_line, re.IGNORECASE)
    coord_str = " ".join([f"{ax}{val}" for ax, val in coords])

    results = []
    for m_code in movements:
        m = f"G{m_code}"
        desc = descriptions.get(m, "Unknown G-code")
        results.append(f"{m} ({desc}) {coord_str}".strip()) # Add coords if present
    return results


# Extracts the condition from IF(...)
def extract_condition(line):
    match = re.search(r"IF\s*\((.*?)\)\s*(?:GOTOF|GOTO)", line, re.IGNORECASE)
    return match.group(1).strip() if match else None

# Evaluates conditions like ($P_SUBPAR[1]<>FALSE)
def evaluate_condition(condition_str, variables, status_callback):
    # Make replacements case-insensitive if needed, e.g., lowercasing parts
    processed_condition = condition_str.replace("<>", "!=").replace("=", "==") # Replace NC comparison
    # Handle common issue: single '=' for comparison
    processed_condition = re.sub(r'(?<![<>!=])=(?!=)', '==', processed_condition)

    # Substitute array syntax like $P_SUBPAR[1] BEFORE substituting simple vars
    def replace_array_var(match):
        var_name = match.group(1)
        index_part = match.group(2)
        # Try to evaluate the index part if it's a variable itself
        try:
            # Evaluate index expression using current variables
            index_val_str = evaluate_expression(index_part, variables, status_callback, is_sub_eval=True)
            index_val = int(float(index_val_str)) # Convert evaluated result to int index
            full_var_name = f"{var_name}[{index_val}]"
            return variables.get(full_var_name, "False") # Default to False if index not set
        except Exception as e:
            status_callback(f"⚠️ Index eval error for {var_name}[{index_part}]: {e}")
            # Attempt to use index_part directly if it's a number, else default
            if index_part.isdigit():
                 full_var_name = f"{var_name}[{int(index_part)}]"
                 return variables.get(full_var_name, "False")
            return "False" # Default if index cannot be resolved

    processed_condition = re.sub(r"(\$P_SUBPAR)\[(.*?)\]", replace_array_var, processed_condition, flags=re.IGNORECASE)
    processed_condition = re.sub(r"(\$\w+)\[(.*?)\]", replace_array_var, processed_condition) # General array vars if any

    # Substitute TRUE/FALSE (case-insensitive)
    processed_condition = re.sub(r'\bTRUE\b', 'True', processed_condition, flags=re.IGNORECASE)
    processed_condition = re.sub(r'\bFALSE\b', 'False', processed_condition, flags=re.IGNORECASE)

    # Substitute simple variables (longest names first to avoid partial matches like VAR vs VAR1)
    # Ensure keys are strings before sorting by length
    safe_vars = {k: v for k, v in variables.items() if isinstance(k, str)}
    for var, val in sorted(safe_vars.items(), key=lambda item: len(item[0]), reverse=True):
         # Use word boundaries to avoid replacing parts of other words/numbers
         pattern = r'\b{}\b'.format(re.escape(var))
         # Make sure the value is a valid Python literal (e.g., strings quoted if necessary)
         # Simple heuristic: if it doesn't look like a number or bool, treat as potentially needing quotes
         replacement_val = val
         try:
             # Test if it's a number or boolean directly
             eval(val)
         except:
              # If eval fails, it might be a string that needs quotes or is already quoted
              if not (val.startswith("'") and val.endswith("'")) and not (val.startswith('"') and val.endswith('"')):
                   # It's likely an unquoted string, skip replacement or handle carefully
                   # For safety in eval, might be better to skip or error here
                   # status_callback(f"⚠️ Skipping potentially unsafe substitution for {var}={val}")
                   continue # Skip this substitution for safety in eval

         # Perform the substitution (case-insensitive if needed for var names)
         processed_condition = re.sub(pattern, replacement_val, processed_condition, flags=re.IGNORECASE if var.startswith('$') else 0) # Example: $ vars case-insensitive

    try:
        # Whitelist safe functions/operators for eval if security is a concern
        # For now, assume controlled input or accept the risk of eval
        result = eval(processed_condition, {"__builtins__": {}}, {}) # VERY restricted eval
        # Or a slightly safer eval:
        # safe_globals = {"True": True, "False": False, "abs": abs, "round": round}
        # result = eval(processed_condition, {"__builtins__": None}, safe_globals)
        status_callback(f"🧠 Evaluating: [{condition_str}] -> [{processed_condition}] = {result}")
        return bool(result)
    except Exception as e:
        status_callback(f"❌ Evaluation error: [{processed_condition}] -> {e}")
        return False


# Extract destination label from GOTOF/GOTO (case-insensitive)
def extract_goto_destination(line):
    match = re.search(r"(?:GOTOF|GOTO)\s+(LBL\d+)", line, re.IGNORECASE)
    return match.group(1) if match else None

# Finds the line index of the label like LBL201: (case-insensitive label match)
def find_label_destination(content, label, status_callback):
    label_pattern = re.compile(rf"^\s*{label}\s*:", re.IGNORECASE)
    for idx, line in enumerate(content):
        if label_pattern.match(line.strip()):
            return idx
    status_callback(f"⚠️ Label {label} not found.")
    return len(content) # Go to end if not found

# Process assignment like VAR = EXPR (handle case variations)
def update_variables(line, variables, status_callback):
    # Allow spaces around =, handle different variable name styles
    match = re.match(r"\s*([\w$]+(?:\[.*?\])?)\s*=\s*(.*)", line.strip(), re.IGNORECASE)
    if match:
        var_name = match.group(1).upper() # Normalize variable names (e.g., to uppercase)
        expr_str = match.group(2).strip()
        value = evaluate_expression(expr_str, variables, status_callback)
        variables[var_name] = value # Store with normalized name
        status_callback(f"  Assignment: {var_name} = {value} (from '{expr_str}')")
    return variables


# Evaluate expressions (supports ABS, ROUND, basic arithmetic) (case-insensitive functions)
def evaluate_expression(expr, variables, status_callback, is_sub_eval=False):
    processed_expr = expr.replace("<>", "!=") # NC comparison

    # Substitute array variables first
    def replace_array_var_expr(match):
        var_name = match.group(1)
        index_part = match.group(2)
        try:
            # Recursively evaluate index if it's an expression/variable itself
            index_val_str = evaluate_expression(index_part, variables, status_callback, is_sub_eval=True)
            index_val = int(float(index_val_str)) # Ensure index is integer
            full_var_name = f"{var_name.upper()}[{index_val}]" # Use normalized name
            return variables.get(full_var_name, "0") # Default to "0" if not found? Or raise error?
        except Exception as e:
            # Try direct numeric index if evaluation fails
            if index_part.isdigit():
                 full_var_name = f"{var_name.upper()}[{int(index_part)}]"
                 return variables.get(full_var_name, "0")
            if not is_sub_eval: status_callback(f"⚠️ Index error in expr for {var_name}[{index_part}]: {e}")
            return "0" # Default value on error

    # Apply array substitution (e.g., $P_SUBPAR[...], VAR[...]) - case insensitive var names?
    processed_expr = re.sub(r"(\$P_SUBPAR)\[(.*?)\]", replace_array_var_expr, processed_expr, flags=re.IGNORECASE)
    processed_expr = re.sub(r"(\b\w+)\[(.*?)\]", replace_array_var_expr, processed_expr) # General array vars


    # Substitute simple variables (longest first, case sensitive/insensitive as needed)
    # Normalize variable names from dict keys before sorting/replacing
    safe_vars = {k: v for k, v in variables.items() if isinstance(k, str)}
    for var, val in sorted(safe_vars.items(), key=lambda item: len(item[0]), reverse=True):
         # Use word boundaries; handle case sensitivity based on var type ($ = insensitive?)
         pattern = r'\b{}\b'.format(re.escape(var))
         flags = re.IGNORECASE if var.startswith('$') else 0
         # Be careful about replacing with strings that break the expression.
         # If val is not a number, it might need special handling (e.g., keep as is if it's a function name?)
         # This simple replacement is risky if variables hold non-numeric strings.
         processed_expr = re.sub(pattern, str(val), processed_expr, flags=flags)

    # Replace function names (case-insensitive)
    processed_expr = re.sub(r'\bABS\b', 'abs', processed_expr, flags=re.IGNORECASE)
    processed_expr = re.sub(r'\bROUND\b', 'round', processed_expr, flags=re.IGNORECASE)
    # Add more functions here: SQRT -> math.sqrt, SIN -> math.sin etc. Need import math
    # Need to provide these functions to eval's context

    try:
        # Use a safer eval environment
        safe_globals = {
            "abs": abs,
            "round": round,
            # "math": math # If functions like sqrt, sin are needed
        }
        # Add current variable values (numerics only?) to locals for safety
        safe_locals = {}
        for k, v in variables.items():
             try:
                 safe_locals[k] = float(v) # Try converting to float for eval
             except (ValueError, TypeError):
                 # Handle non-numeric variables if necessary, maybe pass as strings?
                 # Or ignore them for arithmetic eval
                 pass

        # Evaluate the processed expression
        result = eval(processed_expr, {"__builtins__": None}, safe_globals) # Add safe_locals if needed by expr
        return str(result)
    except Exception as e:
        if not is_sub_eval: status_callback(f"❌ Expression error: [{expr}] -> [{processed_expr}] -> {e}")
        return expr # Return original expression on error

# Assign arguments like BP_1, BP_2 and also $P_SUBPAR[n]
def bind_arguments(args, status_callback):
    vars_dict = {}
    if args is None:
        status_callback("❌ Error: No arguments provided for binding.")
        return vars_dict

    for i, arg in enumerate(args):
        bp_name = f"BP_{i + 1}"
        subpar_name = f"$P_SUBPAR[{i + 1}]" # Use normalized name convention

        if arg is not None:
            vars_dict[bp_name] = str(arg) # Store as string initially
            vars_dict[subpar_name] = "True"
        else:
            # Handle missing arguments - default or error?
            # For GUI, we assume they MUST be provided in the call string.
            # Assigning a default or placeholder might be an option.
            vars_dict[bp_name] = "0" # Default to "0" or some indicator?
            vars_dict[subpar_name] = "False"
            status_callback(f"⚠️ Missing argument {i+1}, using default for {bp_name} and {subpar_name}=False")

    status_callback(f"  Bound arguments: {len(args)} found.")
    return vars_dict


# --- Tkinter GUI Class ---

class NC_Debugger_GUI:
    def __init__(self, master):
        self.master = master
        master.title("NC Code Debugger")
        master.geometry("900x700")

        # Configure Fonts
        self.mono_font = font.Font(family="Courier New", size=10)
        self.status_font = font.Font(family="Segoe UI", size=9)

        # --- State Variables ---
        self.program_content = []
        self.current_line_index = 0
        self.variables = {}
        self.movements = []
        self.current_func_name = ""
        self.simulation_active = False
        self.subprograms_called = set() # Reset per session


        # --- GUI Layout ---
        # Top Frame: Input and Controls
        top_frame = tk.Frame(master, pady=5)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Function Call:").pack(side=tk.LEFT, padx=5)
        self.call_entry = tk.Entry(top_frame, width=50)
        self.call_entry.pack(side=tk.LEFT, padx=5)
        self.call_entry.insert(0, DEFAULT_CALL)

        self.load_button = tk.Button(top_frame, text="Load", command=self.load_program)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.step_button = tk.Button(top_frame, text="Step", command=self.step_execution, state=tk.DISABLED)
        self.step_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(top_frame, text="Reset", command=self.reset_simulation, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Main Area: Code, Variables, Movements (using PanedWindow for resizing)
        main_pane = tk.PanedWindow(master, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bd=2)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left Pane: Code View
        code_frame = tk.Frame(main_pane, bd=1, relief=tk.SUNKEN)
        tk.Label(code_frame, text="Program Code").pack(fill=tk.X)
        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, font=self.mono_font, height=20, width=70)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.tag_configure("highlight", background="yellow", borderwidth=1, relief=tk.RAISED)
        self.code_text.config(state=tk.DISABLED) # Read-only
        main_pane.add(code_frame, stretch="always")


        # Right Pane: Variables and Movements (using another PanedWindow)
        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, sashrelief=tk.RAISED, bd=2)
        main_pane.add(right_pane, stretch="never") # Adjust stretch as needed

        # Variable View
        var_frame = tk.Frame(right_pane, bd=1, relief=tk.SUNKEN)
        tk.Label(var_frame, text="Variables").pack(fill=tk.X)
        self.var_text = scrolledtext.ScrolledText(var_frame, wrap=tk.NONE, font=self.mono_font, height=10, width=40) # No wrap is better for vars
        self.var_text.pack(fill=tk.BOTH, expand=True)
        self.var_text.config(state=tk.DISABLED) # Read-only
        right_pane.add(var_frame, stretch="always")


        # Movement Log
        move_frame = tk.Frame(right_pane, bd=1, relief=tk.SUNKEN)
        tk.Label(move_frame, text="Movement Log").pack(fill=tk.X)
        self.move_text = scrolledtext.ScrolledText(move_frame, wrap=tk.WORD, font=self.mono_font, height=10, width=40)
        self.move_text.pack(fill=tk.BOTH, expand=True)
        self.move_text.config(state=tk.DISABLED) # Read-only
        right_pane.add(move_frame, stretch="always")


        # Status Bar
        self.status_label = tk.Label(master, text="Status: Ready. Enter function call and press Load.", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.status_font)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    # --- GUI Methods ---

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        self.master.update_idletasks() # Force GUI update

    def load_program(self):
        self.reset_simulation(clear_call=False) # Reset state but keep call text
        self.subprograms_called = set() # Clear called set for new run
        call_str = self.call_entry.get()
        if not call_str:
            messagebox.showerror("Error", "Please enter a function call.")
            return

        func_name, args = parse_call(call_str)
        if not func_name:
            messagebox.showerror("Error", f"Invalid call format: {call_str}\nUse: BPxxxx(...)")
            return

        self.update_status(f"Parsing call: {func_name}, Args: {args}")
        self.program_content = read_file(func_name, self.update_status)

        if self.program_content:
            self.current_func_name = func_name
            self.variables = bind_arguments(args, self.update_status) # Bind initial args
            self.current_line_index = 0
            self.simulation_active = True

            # Display code
            self.code_text.config(state=tk.NORMAL)
            self.code_text.delete('1.0', tk.END)
            for i, line in enumerate(self.program_content):
                self.code_text.insert(tk.END, f"{i+1:04d}: {line}") # Add line numbers
            self.code_text.config(state=tk.DISABLED)

            self.update_variable_display()
            self.update_movement_log() # Clear log initially
            self.highlight_line()

            self.step_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.DISABLED) # Prevent reloading mid-session
            self.update_status(f"Loaded {func_name}. Ready to Step.")
        else:
            messagebox.showerror("Error", f"Could not load program: {func_name}. Check console/status.")
            self.reset_simulation()

    def step_execution(self):
        if not self.simulation_active or self.current_line_index >= len(self.program_content):
            self.update_status("Simulation finished or not active.")
            self.step_button.config(state=tk.DISABLED)
            return

        line_num = self.current_line_index
        line = self.program_content[line_num].strip()

        self.update_status(f"Executing line {line_num + 1}: {line}")
        self.highlight_line() # Highlight before execution

        # --- Simulation Logic (Adapted from simulate_execution) ---
        jumped = False
        next_line_index = self.current_line_index + 1 # Default next line

        # Skip comments or empty lines (optional)
        if not line or line.startswith(';') or line.startswith('%'):
             self.update_status(f"Skipping comment/empty line {line_num + 1}")

        # Conditional jump (IF ... GOTO / GOTOF)
        elif "IF" in line.upper() and ("GOTO" in line.upper() or "GOTOF" in line.upper()):
            condition_str = extract_condition(line)
            destination = extract_goto_destination(line)

            if condition_str and destination:
                result = evaluate_condition(condition_str, self.variables, self.update_status)
                self.update_status(f"Condition '{condition_str}' -> {result}")

                if "GOTOF" in line.upper(): # Jump if False
                    if not result:
                        target_idx = find_label_destination(self.program_content, destination, self.update_status)
                        self.update_status(f"Condition False, jumping to {destination} (line ~{target_idx + 1})")
                        next_line_index = target_idx
                        jumped = True
                    else:
                        self.update_status("Condition True, GOTOF proceeds to next line.")
                elif "GOTO" in line.upper(): # Jump if True (often just GOTO follows IF)
                    if result:
                         target_idx = find_label_destination(self.program_content, destination, self.update_status)
                         self.update_status(f"Condition True, jumping to {destination} (line ~{target_idx + 1})")
                         next_line_index = target_idx
                         jumped = True
                    else:
                         self.update_status("Condition False, conditional GOTO proceeds to next line.")
            else:
                 self.update_status(f"⚠️ Malformed IF/GOTO line: {line}")


        # Unconditional jump (GOTO LBLx) - check if not part of IF
        elif re.match(r"^\s*GOTO\s+(LBL\d+)", line, re.IGNORECASE) and "IF" not in line.upper():
             destination = extract_goto_destination(line)
             if destination:
                 target_idx = find_label_destination(self.program_content, destination, self.update_status)
                 self.update_status(f"Unconditional jump to {destination} (line ~{target_idx + 1})")
                 next_line_index = target_idx
                 jumped = True
             else:
                  self.update_status(f"⚠️ Malformed GOTO line: {line}")

        # Movement command (G-code)
        elif re.search(r'\bG[0-9]+', line): # Basic check for G codes
            move_info = extract_movements(line)
            if move_info:
                for move in move_info:
                    self.movements.append(f"L{line_num+1}: {move}")
                    self.update_status(f"Movement detected: {move}")
                self.update_movement_log()

        # Assignment (=)
        elif "=" in line:
            self.variables = update_variables(line, self.variables, self.update_status)
            self.update_variable_display()

        # Subprogram call (basic handling)
        elif re.search(r"BP\d+\(", line, re.IGNORECASE):
            # This is simplified: it logs the call but doesn't step *into* it.
            # A full implementation would need a call stack and loading the new program.
            called_match = re.search(r"(BP\d+)\((.*)\)", line, re.IGNORECASE)
            if called_match:
                 sub_func = called_match.group(1).upper()
                 sub_args_str = called_match.group(2) # Arguments not evaluated here yet
                 if sub_func not in self.subprograms_called:
                      self.update_status(f"📞 Calling subprogram: {sub_func}({sub_args_str}) (Step-into not implemented)")
                      self.subprograms_called.add(sub_func)
                      # Here you *could* recursively call simulate/step or push onto a stack
                 else:
                      self.update_status(f"🔁 Subprogram {sub_func} already called/visited. Skipping.")
            else:
                 self.update_status(f"⚠️ Found potential subprogram call, but couldn't parse: {line}")


        # Label definition (LBLx:) - usually just proceed
        elif re.match(r"^\s*LBL\d+\s*:", line, re.IGNORECASE):
             self.update_status(f"Label found: {line.strip()}")
             # No action needed, just proceeds to next line

        # End of program
        if "M30" in line.upper() or "M17" in line.upper():
            self.update_status("🏁 Program end (M30/M17) reached.")
            self.simulation_active = False
            self.step_button.config(state=tk.DISABLED)
            # Don't advance index beyond end
            return # Stop processing further on this step


        # --- Update state for next step ---
        self.current_line_index = next_line_index

        # Check if simulation should end after update
        if self.current_line_index >= len(self.program_content):
            self.update_status("🏁 Reached end of file.")
            self.simulation_active = False
            self.step_button.config(state=tk.DISABLED)


    def update_variable_display(self):
        self.var_text.config(state=tk.NORMAL)
        self.var_text.delete('1.0', tk.END)
        if self.variables:
            # Sort for consistency, perhaps? (e.g., BP_, then $, then others)
            sorted_vars = sorted(self.variables.items())
            for key, value in sorted_vars:
                self.var_text.insert(tk.END, f"{key} = {value}\n")
        else:
             self.var_text.insert(tk.END, "(No variables yet)")
        self.var_text.config(state=tk.DISABLED)

    def update_movement_log(self):
        self.move_text.config(state=tk.NORMAL)
        self.move_text.delete('1.0', tk.END)
        if self.movements:
            for move in self.movements:
                self.move_text.insert(tk.END, f"{move}\n")
        else:
             self.move_text.insert(tk.END, "(No movements logged yet)")
        self.move_text.config(state=tk.DISABLED)

    def highlight_line(self):
        if not self.program_content or self.current_line_index >= len(self.program_content):
            return

        # Remove previous highlight
        self.code_text.tag_remove("highlight", "1.0", tk.END)

        # Add new highlight
        line_start = f"{self.current_line_index + 1}.0"
        line_end = f"{self.current_line_index + 1}.end"
        tag_start = f"{self.current_line_index + 1}.6" # Start highlight after line number "xxxx: "

        self.code_text.tag_add("highlight", tag_start, line_end)
        self.code_text.see(line_start) # Scroll to the highlighted line

    def reset_simulation(self, clear_call=True):
        self.program_content = []
        self.current_line_index = 0
        self.variables = {}
        self.movements = []
        self.current_func_name = ""
        self.simulation_active = False
        self.subprograms_called = set()

        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete('1.0', tk.END)
        self.code_text.config(state=tk.DISABLED)

        self.var_text.config(state=tk.NORMAL)
        self.var_text.delete('1.0', tk.END)
        self.var_text.config(state=tk.DISABLED)

        self.move_text.config(state=tk.NORMAL)
        self.move_text.delete('1.0', tk.END)
        self.move_text.config(state=tk.DISABLED)

        if clear_call:
            self.call_entry.delete(0, tk.END)
            # self.call_entry.insert(0, DEFAULT_CALL) # Optionally reset to default

        self.step_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.NORMAL) # Re-enable load

        self.update_status("Ready. Enter function call and press Load.")

# --- Main Execution ---
if __name__ == "__main__":
    # Create the base directory if it doesn't exist
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
        print(f"Created directory: {BASE_PATH}")
        # Optional: Create a dummy program file for testing
        dummy_file = os.path.join(BASE_PATH, "BP9725.nc")
        if not os.path.exists(dummy_file):
            with open(dummy_file, "w") as f:
                f.write(";\n")
                f.write("N10 G0 X10 Y20\n")
                f.write("N20 MY_VAR = 100\n")
                f.write("N30 IF ($P_SUBPAR[1] == TRUE) GOTO LBL1\n") # Corrected ==
                f.write("N40 G1 Z-5 F100\n")
                f.write("N50 GOTO LBL2\n")
                f.write("N60 LBL1:\n")
                f.write("N70 G1 X50 Y50\n")
                f.write("N80 LBL2:\n")
                f.write("N90 MY_VAR = MY_VAR + BP_3\n")
                f.write("N100 G0 Z100\n")
                f.write("N110 IF (MY_VAR > 105) GOTOF LBL3\n")
                f.write("N120 G1 X0 Y0\n")
                f.write("N130 LBL3:\n")
                f.write("N140 M30\n")
            print(f"Created dummy file: {dummy_file}")


    root = tk.Tk()
    gui = NC_Debugger_GUI(root)
    root.mainloop()

'''
**To Use This Code:**

1.  **Save:** Save the code as a Python file (e.g., `nc_debugger_gui.py`).
2.  **Directory:** Make sure you have a directory named `nc_programs` in the *same location* where you save the Python script.
3.  **NC Files:** Place your `.nc` program files (like `BP9725.nc`) inside the `nc_programs` directory. The script includes code to create this directory and a basic `BP9725.nc` file if they don't exist, for demonstration.
4.  **Run:** Execute the script from your terminal: `python nc_debugger_gui.py`
5.  **Interact:**
    * The GUI window will appear.
    * The default function call is pre-filled. You can change it.
    * Click "Load". The NC code should appear in the left pane, initial variables on the right.
    * Click "Step" repeatedly to execute the program line by line.
    * Observe the yellow highlight on the current line in the code view.
    * Watch the "Variables" and "Movement Log" panes update.
    * Check the "Status" bar at the bottom for messages.
    * Click "Reset" to clear everything and load a new program.

This GUI provides a much more visual and interactive way to understand the flow and effects of your NC subprograms.'''