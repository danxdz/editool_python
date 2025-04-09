

import tkinter as tk
from tkinter import scrolledtext, messagebox, font

from constants import BASE_PATH, DEFAULT_CALL

from tools import * 

# --- Tkinter GUI Class ---
class NC_Debugger_GUI:
    # Keep __init__ and GUI Layout
    def __init__(self, master):
        
        self.master=master; master.title("NC Debugger"); master.geometry("1000x800")
        self.mono_font=font.Font(family="Courier New",size=10); self.status_font=font.Font(family="Segoe UI",size=9)
        self.program_content=[]; self.current_line_index=0; self.variables={}; self.movements=[]
        self.current_func_name=""; self.simulation_active=False; self.call_stack=[]
        top=tk.Frame(master,pady=5); top.pack(fill=tk.X,padx=5)
        tk.Label(top,text="Call:").pack(side=tk.LEFT)
        self.call_entry=tk.Entry(top,width=60); self.call_entry.pack(side=tk.LEFT,padx=5,fill=tk.X,expand=True); self.call_entry.insert(0,DEFAULT_CALL)
        self.load_button=tk.Button(top,text="Load",command=self.load_program,width=8); self.load_button.pack(side=tk.LEFT,padx=2)
        # Play Button
        self.play_button = tk.Button(top, text="▶️ Play", command=self.run_until_breakpoint, state=tk.DISABLED, width=8)
        self.play_button.pack(side=tk.LEFT, padx=2)
        self.step_button=tk.Button(top,text="Step",command=self.step_execution,state=tk.DISABLED,width=8); self.step_button.pack(side=tk.LEFT,padx=2)
        self.reset_button=tk.Button(top,text="Reset",command=self.reset_simulation,state=tk.DISABLED,width=8); self.reset_button.pack(side=tk.LEFT,padx=2)
        mpane=tk.PanedWindow(master,orient=tk.HORIZONTAL,sashrelief=tk.RAISED,bd=2); mpane.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        cframe=tk.LabelFrame(mpane,text="Code",bd=1,relief=tk.SUNKEN,padx=2,pady=2)
        self.code_text=scrolledtext.ScrolledText(cframe,wrap=tk.NONE,font=self.mono_font,height=20,width=80); self.code_text.pack(fill=tk.BOTH,expand=True); self.code_text.tag_configure("highlight",background="yellow",borderwidth=1,relief=tk.RAISED); self.code_text.config(state=tk.DISABLED)
        mpane.add(cframe,stretch="always")
        rpane=tk.PanedWindow(mpane,orient=tk.VERTICAL,sashrelief=tk.RAISED,bd=2); mpane.add(rpane,stretch="never",width=350)
        sframe=tk.LabelFrame(rpane,text="Stack",bd=1,relief=tk.SUNKEN,padx=2,pady=2)
        self.stack_text=scrolledtext.ScrolledText(sframe,wrap=tk.NONE,font=self.mono_font,height=6,width=45); self.stack_text.pack(fill=tk.BOTH,expand=True); self.stack_text.config(state=tk.DISABLED)
        rpane.add(sframe,stretch="never",height=120)
        vframe=tk.LabelFrame(rpane,text="Vars",bd=1,relief=tk.SUNKEN,padx=2,pady=2)
        self.var_text=scrolledtext.ScrolledText(vframe,wrap=tk.NONE,font=self.mono_font,height=15,width=45); self.var_text.pack(fill=tk.BOTH,expand=True); self.var_text.config(state=tk.DISABLED)
        rpane.add(vframe,stretch="always")
        mframe=tk.LabelFrame(rpane,text="Moves",bd=1,relief=tk.SUNKEN,padx=2,pady=2)
        self.move_text=scrolledtext.ScrolledText(mframe,wrap=tk.NONE,font=self.mono_font,height=10,width=45); self.move_text.pack(fill=tk.BOTH,expand=True); self.move_text.config(state=tk.DISABLED)
        rpane.add(mframe,stretch="always")
        self.status_label=tk.Label(master,text="Status: Ready.",bd=1,relief=tk.SUNKEN,anchor=tk.W,font=self.status_font); self.status_label.pack(side=tk.BOTTOM,fill=tk.X,padx=5,pady=2)
        # Breakpoint tracking
        self.breakpoints = set()



    # --- GUI Methods  ---

    def run_until_breakpoint(self):
        while self.simulation_active and self.current_line_index < len(self.program_content):
            if self.current_line_index in self.breakpoints:
                self.update_status(f"⛔ Breakpoint hit at L{self.current_line_index+1}")
                break
            prev_idx = self.current_line_index
            self.step_execution()
            if self.current_line_index == prev_idx:
                break  # Prevents infinite loop if stuck



    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}"); print(f"DEBUG: {message}"); self.master.update_idletasks()
    def update_code_display(self):
        self.code_text.config(state=tk.NORMAL); self.code_text.delete('1.0', tk.END)
        parent=self.code_text.master; title=f"Code: {self.current_func_name}.nc" if self.current_func_name else "Code"
        if isinstance(parent, tk.LabelFrame): parent.config(text=title)
        if self.program_content:
            for i, line in enumerate(self.program_content): self.code_text.insert(tk.END, f"{i+1:04d}: {line}")
        self.code_text.config(state=tk.DISABLED); self.highlight_line()

        self.code_text.tag_configure("breakpoint", background="#FFB3B3")  # light red

        for i, line in enumerate(self.program_content):
            if i in self.breakpoints:
                self.code_text.tag_add("breakpoint", f"{i+1}.0", f"{i+1}.end")

    def update_call_stack_display(self):
        self.stack_text.config(state=tk.NORMAL); self.stack_text.delete('1.0', tk.END)
        if not self.call_stack: self.stack_text.insert('1.0', "(Stack Empty)")
        else: # Display simplified stack: (caller_func_name, caller_content, caller_return_line_idx)
            for i,(f,_,r) in reversed(list(enumerate(self.call_stack))): self.stack_text.insert('1.0', f"{i}:{f}(ret L{r+1})\n")
        self.stack_text.config(state=tk.DISABLED)
    def load_program(self):
        self.reset_simulation(False); call_str=self.call_entry.get()
        if not call_str: messagebox.showerror("Error", "Enter call."); return
        func, args, err = parse_call(call_str)
        if err: messagebox.showerror("Error", err); return
        self.update_status(f"Loading: {func}"); content=read_file(func, self.update_status)
        if content:
            self.program_content=content; self.current_func_name=func; self.current_line_index=0
            self.variables = {}; self.variables = bind_arguments(args, self.variables, self.update_status, False);
            self.simulation_active=True; 
            self.update_displays();
            self.step_button.config(state=tk.NORMAL); 
            self.reset_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.DISABLED); 
            self.update_status(f"Loaded {func}. Ready.")
            self.play_button.config(state=tk.NORMAL)  # Enable play button after loading
        else: messagebox.showerror("Error", f"Load fail: {func}."); self.reset_simulation()
    def update_variable_display(self):
        self.var_text.config(state=tk.NORMAL); self.var_text.delete('1.0', tk.END)
        if self.variables:
            for k,v in sorted(self.variables.items()): self.var_text.insert(tk.END, f"{k} = {v}\n")
        else: self.var_text.insert('1.0', "(No vars)")
        self.var_text.config(state=tk.DISABLED); self.var_text.yview_moveto(0)
    def update_movement_log(self):
        self.move_text.config(state=tk.NORMAL); self.move_text.delete('1.0', tk.END)
        if self.movements:
            for m in self.movements: self.move_text.insert(tk.END, f"{m}\n")
        else: self.move_text.insert('1.0', "(No movements)")
        self.move_text.config(state=tk.DISABLED); self.move_text.see(tk.END)
    def highlight_line(self):
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        if not self.program_content or self.current_line_index >= len(self.program_content): return
        ls=f"{self.current_line_index+1}.0"; le=f"{self.current_line_index+1}.end"; ts=f"{self.current_line_index+1}.6"
        try: self.code_text.tag_add("highlight", ts, le); self.code_text.see(ls)
        except tk.TclError: self.update_status(f"⚠️ Highlight Err L{self.current_line_index+1}")
    
    

    def reset_simulation(self, clear_call=True):
        # Only clear simulation-related variables (not the function call text)
        self.variables = {}
        self.movements = []
        self.call_stack = []

        # Reset other simulation-related variables
        self.current_line_index = 0
        self.simulation_active = False

        # Update displays without clearing the function call entry
        self.update_displays()

        # Optionally clear the content of other textboxes (e.g., variables, movements, stack)
        for w in [self.var_text, self.move_text, self.stack_text]:
            w.config(state=tk.NORMAL)
            w.delete('1.0', tk.END)
            w.config(state=tk.DISABLED)

        # Update the function name label in the code textbox, if needed
        p = self.code_text.master
        if isinstance(p, tk.LabelFrame): 
            p.config(text="Code" if not self.current_func_name else f"Code: {self.current_func_name}")

        # Reset the variables, movements, and stack displays
        self.var_text.config(state=tk.NORMAL)
        self.var_text.insert('1.0', "(No vars)" if not self.variables else "")
        self.var_text.config(state=tk.DISABLED)

        self.move_text.config(state=tk.NORMAL)
        self.move_text.insert('1.0', "(No moves)" if not self.movements else "")
        self.move_text.config(state=tk.DISABLED)

        self.stack_text.config(state=tk.NORMAL)
        self.stack_text.insert('1.0', "(Stack Empty)" if not self.call_stack else "")
        self.stack_text.config(state=tk.DISABLED)

        # Optionally clear the call entry if needed
        if clear_call:
            self.call_entry.delete(0, tk.END)

        # Ensure the call entry text persists and is not cleared
        self.call_entry.config(state=tk.NORMAL)
        # Do not clear the call entry content
        self.call_entry.config(state=tk.DISABLED)

        # Disable buttons after reset
        self.step_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.NORMAL)
        self.update_status("Ready.")
        self.play_button.config(state=tk.DISABLED)  # Disable play button on reset



    def handle_m30(self):
        self.update_status("🏁 M30 End."); self.simulation_active=False; self.step_button.config(state=tk.DISABLED)
        self.call_stack=[]; self.update_call_stack_display()
    def handle_subprogram_call(self, line):
        call_match=re.search(r"\b(BP\d+\s*\(.*\))", line, re.IGNORECASE); actual_call=None
        if call_match: actual_call = call_match.group(1)
        else:
            m=re.search(r"\b(BP\d+)\b", line, re.IGNORECASE)
            if m: actual_call = m.group(1)+"()" # Add () if missing
            else: self.update_status(f"⚠️ Sub Call Pattern Fail: {line}"); return False
        sub_f, args_l, err = parse_call(actual_call)
        if err: self.update_status(f"❌ Sub Arg Parse Err: {err}"); return False
        content = read_file(sub_f, self.update_status)
        if content:
            ret_idx = self.current_line_index+1; self.call_stack.append((self.current_func_name, self.program_content, ret_idx))
            self.update_call_stack_display(); self.current_func_name=sub_f; self.program_content=content
            self.current_line_index=0; self.variables=bind_arguments(args_l, self.variables, self.update_status, True) # Shared scope
            self.update_displays(); return True
        else: self.update_status(f"⚠️ Sub Load Fail: {sub_f}. Skip."); return False
    def handle_return(self, is_m17):
        if self.call_stack:
            c_f, c_c, c_r = self.call_stack.pop(); self.update_call_stack_display()
            self.current_func_name=c_f; self.program_content=c_c; self.current_line_index=c_r
            self.update_displays(); self.update_status(f"↩️ Return to {c_f} L{c_r+1}"); return True
        else:
            stat="⚠️ M17/RET Base." if is_m17 else "🏁 End Base."
            self.update_status(stat+" Stop."); self.simulation_active=False; self.step_button.config(state=tk.DISABLED); return False
    def handle_assignment(self, line):
        self.variables = update_variables(line, self.variables, self.update_status); self.update_variable_display()
    def handle_movement(self, line, line_num):
        moves=extract_movements(line);
        if moves:
            prefix=f"L{line_num+1}({self.current_func_name}):"
            for m in moves: self.movements.append(f"{prefix} {m}")
            self.update_movement_log()
    def end_of_program_check(self):
        if self.call_stack: self.handle_return(False)
        else: self.update_status("🏁 End Base."); self.simulation_active=False; self.step_button.config(state=tk.DISABLED)
    def update_displays(self):
        self.update_code_display(); self.update_variable_display(); self.update_movement_log(); self.update_call_stack_display()

    # --- REVISED Jump Handlers ---
    def handle_conditional_jump(self, line, upper_line, line_num):
        """Handles IF [opt_paren] (...) [opt_paren] GOTOx LBL logic."""
        next_idx = line_num + 1
        jumped = False
        condition_str = None
        # Regex: Find IF, optionally capture outer parens, capture condition (non-greedy), optional THEN, GOTOx (all types), Label/Destination
        if_pattern = r"^\s*(?:\w+\s*:+\s*)?IF\s*(\()?(.+?)(\))?\s*(?:THEN\s+)?(GOTOB|GOTOF|GOTO|GOTOC)\s+(.+?)\s*$"

        match = re.match(if_pattern, line, re.IGNORECASE | re.DOTALL)

        if match:
            groups = match.groups()
            if len(groups) == 6:
                open_p, condition_str, close_p, then_found, jump_command, destination = groups
            else:
                open_p, condition_str, close_p, jump_command, destination = groups
                then_found = None

            condition_str = condition_str.strip()

            if condition_str:
                result = evaluate_condition(condition_str, self.variables, self.update_status)
                take_jump = False  # Initialize take_jump

                if jump_command.upper() in ["GOTOB", "GOTOF", "GOTO", "GOTOC"]:
                    if result:
                        take_jump = True

                if take_jump:
                    # Check if the destination label is a calculated expression (e.g., "LBL" + expression)
                    if isinstance(destination, str) and "<<" in destination:  # This checks if it has a concatenation operator
                        try:
                            # Remove the "LBL" part, evaluate the numeric expression inside, and then reconstruct the label
                            expression = destination.replace("<<", "").strip()
                            evaluated_value = eval(expression, {}, self.variables)  # Evaluate the expression inside
                            destination_label = f"LBL{int(evaluated_value)}"  # Ensure label is formatted properly
                            self.update_status(f"✅ Computed destination label: {destination_label}")
                        except Exception as e:
                            self.update_status(f"❌ Error evaluating label expression: {destination} → {e}")
                            destination_label = None  # Set to None if error in evaluation
                    else:
                        destination_label = destination.strip()  # No expression, just use the label directly
                    
                    # Handle the jump to the computed label
                    if destination_label:
                        if jump_command.upper() == "GOTOB":
                            target_idx = find_label_backward(self.program_content, destination_label, line_num, self.update_status)
                        else:  # GOTOF, GOTO, GOTOC (forward or search)
                            target_idx = find_label_forward(self.program_content, destination_label, line_num, self.update_status)

                        if target_idx is not None:  # If the target label was found, proceed with the jump
                            next_idx = target_idx
                            jumped = True
                        else:
                            self.update_status(f"⚠️ Label '{destination_label}' not found.")
                    else:
                        self.update_status(f"⚠️ Invalid destination label: {destination_label}")
                else:
                    self.update_status(f"⚠️ IF condition evaluated to False, no jump.")
            else:
                self.update_status(f"⚠️ IF condition extracted empty: {line}")
        else:
            if upper_line.startswith("IF"):
                self.update_status(f"  Info: IF line pattern not matched: {line}")

        return next_idx, jumped



    def handle_unconditional_jump(self, upper_line, line_num, jump_mode):
        """Handles GOTOF, GOTOB, GOTO LBL."""
        jump_type = "GOTO" + (jump_mode if jump_mode != "A" else "")
        next_idx = line_num + 1
        jumped = False

        # Match a static label (e.g., LBL1234)
        dest_match = re.match(rf"{jump_type}\s+(LBL\d+)", upper_line, re.IGNORECASE)

        if dest_match:
            dest = dest_match.group(1)  # Static label like LBL1234
            if jump_mode == "F":
                target_idx = find_label_forward(self.program_content, dest, line_num, self.update_status)
            elif jump_mode == "B":
                target_idx = find_label_backward(self.program_content, dest, line_num, self.update_status)
            else:  # Default GOTO
                target_idx = find_label_forward(self.program_content, dest, line_num, self.update_status)
            next_idx = target_idx
            jumped = True
        else:
            # Handle dynamic label expression (e.g., LBL << (2000 + BP_1))
            expr_match = re.match(rf"{jump_type}\s+(LBL)<<\s*\((.*)\)\s*$", upper_line, re.IGNORECASE)
            if expr_match:
                label_base = expr_match.group(1)  # LBL
                expr = expr_match.group(2)  # The expression inside (e.g., 2000 + BP_1)
                try:
                    # Define safe globals for eval() to handle mathematical functions
                    safe_globals = {
                        "__builtins__": None,
                        "int": int, "float": float, "abs": abs,
                        "round": round, "bool": bool, "True": True, "False": False,
                        "trunc": math.trunc, "ABS": abs, "TRUNC": math.trunc
                    }

                    # Replace any non-numeric or non-safe characters in the expression (optional)
                    expr = expr.replace("<>", "!=").replace("===", "==").replace("=>", ">=")

                    # Evaluate the expression (e.g., 2000 + BP_1)
                    eval_expr = eval(expr, safe_globals, self.variables)
                    computed_label = f"{label_base}{int(eval_expr)}"  # Form the full label like LBL2101

                    # Now find the target index using the computed label
                    if jump_mode == "F":
                        target_idx = find_label_forward(self.program_content, computed_label, line_num, self.update_status)
                    elif jump_mode == "B":
                        target_idx = find_label_backward(self.program_content, computed_label, line_num, self.update_status)
                    else:
                        target_idx = find_label_forward(self.program_content, computed_label, line_num, self.update_status)
                    next_idx = target_idx
                    jumped = True
                except Exception as e:
                    self.update_status(f"❌ Error evaluating expression for label: {expr} → {e}")
            else:
                self.update_status(f"⚠️ Malformed {jump_type}: {upper_line}")

        return next_idx, jumped


    # --- Main Step Execution Logic ---
    def step_execution(self):
        if not self.simulation_active: self.update_status("Sim inactive."); return #
        if self.current_line_index >= len(self.program_content): self.end_of_program_check(); return
        line_num = self.current_line_index
        try: line = self.program_content[line_num].strip(); upper_line = line.upper()
        except IndexError: self.update_status(f"❌ IE: Idx {line_num}"); self.simulation_active=False; return

        self.highlight_line()
        self.update_status(f"Exec L{line_num + 1} ({self.current_func_name}): {line[:90]}")

        next_line_index = self.current_line_index + 1
        jumped = False; call_occurred = False; return_occurred = False; handled = False

        try:
            # --- Execution Logic (Ordered and Refined) ---
            if not line or line.startswith(';') or line.startswith('%'): handled = True # 1. Skip comment/empty
            elif "M17" in upper_line: return_occurred = self.handle_return(is_m17=True); handled = True # 2. Returns/Ends
            elif upper_line.startswith("RET"): return_occurred = self.handle_return(is_m17=False); handled = True
            elif "M30" in upper_line: self.handle_m30(); return

            # Check specific commands before general patterns
            # --- Computed GOTO Handling ---
            elif (comp_goto := re.match(r'^\s*(GOTOF|GOTO)\s+"LBL"<<\s*\((.*)\)', line, re.IGNORECASE)): # 5. Computed GOTO
                handled = True
                jump_mode_comp = "F" if comp_goto.group(1).upper() == "GOTOF" else "A"
                expr_str = comp_goto.group(2).strip()
                try:
                    lbl_num_str = evaluate_expression(expr_str, self.variables, self.update_status)
                    lbl_num = int(float(lbl_num_str))
                    dest_lbl = f"LBL{lbl_num}"
                    self.update_status(f"  Computed GOTO{jump_mode_comp} to {dest_lbl} (Expr: {expr_str})")
                    target_idx = find_label_forward(self.program_content, dest_lbl, line_num, self.update_status)
                    next_line_index = target_idx; jumped = True
                except Exception as e: self.update_status(f"❌ Comp GOTO Err: [{expr_str}] -> {e}")

            # --- MSG Handling ---
            elif upper_line.startswith("MSG("): # 6. MSG Command
                handled = True
                msg_match = re.match(r'MSG\s*\((.*)\)', line, re.IGNORECASE)
                msg_content = msg_match.group(1).strip() if msg_match else line[4:].strip()
                final_msg = ""
                # Handle string concatenation ("<<") manually for messages
                parts = []
                current_part = ""
                in_quotes = False
                # Simple split based on << OUTSIDE quotes
                for char in msg_content:
                     if char == '"': in_quotes = not in_quotes; current_part += char
                     elif char == '<' and not in_quotes and current_part.endswith('<'): current_part = current_part[:-1]; parts.append(current_part); current_part = "" # Found <<
                     else: current_part += char
                parts.append(current_part) # Add last part

                for i, part in enumerate(parts):
                    part = part.strip()
                    if part.startswith('"') and part.endswith('"'): final_msg += part[1:-1] # String literal
                    elif part: # Non-empty part, try evaluating
                         try: final_msg += str(evaluate_expression(part, self.variables, self.update_status))
                         except Exception: final_msg += f"<EvalErr:{part}>"
                self.update_status(f"  💬 MSG: {final_msg}")

            # --- SETAL Handling ---
            elif upper_line.startswith("SETAL("): # Handle SETAL
                 handled = True
                 alarm_match = re.match(r'SETAL\s*\((.*)\)', line, re.IGNORECASE)
                 alarm_num_str = alarm_match.group(1).strip() if alarm_match else "?"
                 try: alarm_num = evaluate_expression(alarm_num_str, self.variables, self.update_status); msg = f"Alarm {alarm_num}"
                 except: msg = f"Alarm {alarm_num_str}"
                 self.update_status(f"  🚨 SETAL: {msg} (Simulated: Logged)")

            # Conditional IF checked after specific commands
            if re.search(r"\bIF\s*\(", upper_line, re.IGNORECASE):
                next_line_index, jumped = self.handle_conditional_jump(line, upper_line, line_num)
                handled = True





            # Subprogram calls checked after IF/Computed GOTO
            elif re.search(r"\bBP\d+\s*\(", line): call_occurred = self.handle_subprogram_call(line); handled = True # 3. Sub Calls BPxxx()
            elif re.search(r"\bBP\d+\b", line) and not re.search(r"[=\[]", line): call_occurred = self.handle_subprogram_call(line); handled = True # BPxxx alone

            # Unconditional GOTOx
            elif upper_line.startswith("GOTOF"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "F"); handled = True # 7. GOTOx
            elif upper_line.startswith("GOTOB"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "B"); handled = True
            elif upper_line.startswith("GOTO"): next_line_index, jumped = self.handle_unconditional_jump(upper_line, line_num, "A"); handled = True

            # Loops (Skip)
            elif upper_line.startswith("WHILE"): self.update_status(f"  Skip WHILE (NI): {line}"); handled = True # 8. Loops
            elif upper_line.startswith("ENDWHILE"): self.update_status(f"  Skip ENDWHILE (NI): {line}"); handled = True
            elif upper_line.startswith("LOOP"): self.update_status(f"  Skip LOOP (NI): {line}"); handled = True
            elif upper_line.startswith("ENDLOOP"): self.update_status(f"  Skip ENDLOOP (NI): {line}"); handled = True

            # Assignment
            elif "=" in line: self.handle_assignment(line); handled = True # 9. Assignment

            # G-Codes
            elif upper_line.startswith("G04"): # 10. Dwell
                dwell_m = re.search(r"F([\d\.]+)", upper_line); time = dwell_m.group(1) if dwell_m else "?"
                self.update_status(f"  Dwell G04 F{time} (Skip delay)"); handled = True
            elif re.search(r'\bG[0-9]+\b', line): self.handle_movement(line, line_num); handled = True # 11. Other G

            # Other Skips/Defs
            elif re.match(r"^\s*LBL\d+\s*:", line, re.IGNORECASE): handled = True # 12. Label def
            elif upper_line.startswith("DEF"): handled = True # 13. DEF
            elif upper_line.startswith("STOPRE"): handled = True # 14. STOPRE
            elif re.match(r"^\s*M\d+", upper_line): handled = True # 15. Other M-codes (Skip silently)

            # Unrecognized only if nothing else handled it
            elif not handled : self.update_status(f"  Skip Unrecognized: {line}") # 16. Unrecognized

        except Exception as e:
            self.update_status(f"❌ Runtime Err L{line_num+1}: {e}")
            import traceback; traceback.print_exc()
            pass

        # --- Update state ---
        if not call_occurred and not return_occurred and self.simulation_active:
             self.current_line_index = next_line_index
             if self.current_line_index >= len(self.program_content): self.end_of_program_check()
