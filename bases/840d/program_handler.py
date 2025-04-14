import os
import re

BASE_PATH = "nc_programs"

class ProgramHandler:
    def __init__(self):
        self.channel_1 = []
        self.channel_2 = []
        self.current_step_1 = 0
        self.current_step_2 = 0
        self.loaded_program1 = ""
        self.loaded_program2 = ""
        self.channel_1_file = ""
        self.channel_2_file = ""
        self.ch1_run = True
        self.ch2_run = True
        self.directory = os.path.dirname(__file__)
        self.ch1_stack = []
        self.ch2_stack = []
        self.variables = {}
        self.condition_stack = []
        self.variables["P_SIM"] = True
        self.state = "STOPED"

    def load_program(self, job_file):
        try:
            self.directory = os.path.dirname(job_file)
            with open(job_file, 'r') as file:
                program_data = file.read().splitlines()
                for line in program_data:
                    if "SELECT" in line:
                        parts = line.split()
                        if len(parts) > 1 and parts[1].endswith(".MPF"):
                            if "CH=1" in line:
                                if self.loaded_program1 == "":
                                    self.loaded_program1 = parts[1]
                                self.channel_1_file = parts[1]
                            elif "CH=2" in line:
                                if self.loaded_program2 == "":
                                    self.loaded_program2 = parts[1]
                                self.channel_2_file = parts[1]
            self.load_channel_content(self.directory)
        except FileNotFoundError:
            print(f"Error: File {job_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def load_channel_content(self, directory):
        try:
            if self.channel_1_file:
                path1 = os.path.join(directory, self.channel_1_file)
                if os.path.exists(path1):
                    with open(path1, 'r') as file:
                        self.channel_1 = self._parse_lines(file.read().splitlines())
                else:
                    self.channel_1 = [f"Error: {self.channel_1_file} not found."]
            else:
                self.channel_1 = ["Error: Channel 1 file not specified."]

            if self.channel_2_file:
                path2 = os.path.join(directory, self.channel_2_file)
                if os.path.exists(path2):
                    with open(path2, 'r') as file:
                        self.channel_2 = self._parse_lines(file.read().splitlines())
                else:
                    self.channel_2 = [f"Error: {self.channel_2_file} not found."]
            else:
                self.channel_2 = ["Error: Channel 2 file not specified."]
        except Exception as e:
            print(f"An error occurred while loading files: {e}")

    # Função para extrair o conteúdo do WAITM
    def extrair_conteudo_waitm(self, linha):
        match = re.search(r'WAITM\(([^)]+)\)', linha)
        return match.group(1) if match else None

    def _parse_lines(self, lines):
        """Parse lines of the program, handling variables and conditions."""
        parsed_lines = []
        
        self.condition_stack = []  # Reset condition block
        
        for line in lines:
            clean_line = line.strip()

            if not clean_line or clean_line.startswith(";"):  # Skip empty lines and comments
                continue
            else:
                # Handle condition blocks
                parsed_lines.append(clean_line)
                 

        return parsed_lines

    def run_program(self):
        """Runs both channels until completion."""
        print("Starting program execution...")
        while self.current_step_1 < len(self.channel_1) or self.current_step_2 < len(self.channel_2):
            if self.state == "RUN":
                self.step_execution()
        print("Program execution completed.")

    def reset_simulation(self):
        """Reset the simulation state."""
        self.current_step_1 = 0
        self.current_step_2 = 0
        self.channel_1_file = self.loaded_program1
        self.channel_2_file = self.loaded_program2
        self.variables = {}
        self.subprograms = {}
        self.jump_targets = {}
        #add $P_SIM to variables
        self.variables["$P_SIM"] = True

    def jump_to_label(self, label, channel_number):
        channel = self.channel_1 if channel_number == 1 else self.channel_2
        for idx, line in enumerate(channel):
            if label in line:
                if channel_number == 1:
                    self.current_step_1 = idx
                else:
                    self.current_step_2 = idx
                return True
        return False

    def step_execution(self):
        """Simulate stepping through the program for both channels, independently."""
        self.process_channel_step(1)
        self.process_channel_step(2)
    
    # Replace all variables in the condition with their values
    def var_replacer(self, match, known_vars):
        var_name = match.group(1)  # This will include $ if it's there
        value = known_vars.get(var_name, 0)
        return str(value)


    def process_channel_step(self, channel_number):
        """Process a single step for the given channel (1 or 2)."""
        if channel_number == 1 and self.current_step_1 < len(self.channel_1):
            line = self.channel_1[self.current_step_1]
            current_step = self.current_step_1
            stack = self.ch1_stack
        elif channel_number == 2 and self.current_step_2 < len(self.channel_2):
            line = self.channel_2[self.current_step_2]
            current_step = self.current_step_2
            stack = self.ch2_stack
        else:
            return

        # Check if the line is empty or a comment or /
        if not line or line.startswith(";") or line.startswith("/"):
            # Skip empty lines and comments
            if channel_number == 1:
                self.current_step_1 += 1
            else:
                self.current_step_2 += 1
            return

        # check if theres a ; at middle of the line and remove all after
        if ";" in line:
            line = line.split(";")[0].strip()
            # debug 
            print(f"Channel {channel_number} executing step {current_step + 1}: {line}")



        # Handle GOTO commands
        if "GOTO" in line:
            target_line = self._parse_goto(line)
            if target_line is not None:
                if channel_number == 1:
                    self.current_step_1 = target_line - 1
                else:
                    self.current_step_2 = target_line - 1
                print(f"Channel {channel_number} GOTO to line {target_line}")
                return

        # Handle subprogram calls
        subprogram = self._extract_subprogram_call(line)
        if subprogram:
            print(f"Channel {channel_number} jumping to subprogram {subprogram}")
            if channel_number == 1:
                self.current_step_1 += 1
            else:
                self.current_step_2 += 1
            if self.open_subprogram(subprogram, channel=channel_number):
                print(f"Channel {channel_number} is now executing {subprogram}.SPF")
            return
        
        # Handle machine program calls (Lxxx)
        #if "PROC" not in line and "def" not in line and "L" in line:
            #l_call = re.search(r'\bL(\d{3})\b', line)
        '''
            if l_call:
                l_number = l_call.group(1)
                print(f"Channel {channel_number} calling machine program L{l_number}.")
                if self.open_machine_program(l_number, channel=channel_number):
                    print(f"Channel {channel_number} is now executing L{l_number}.SPF")
                return
        '''
            
        # find parameter RG727 in line test
    
        rg727 = re.search(r'RG727', line)
        if rg727:
            # Extract the value of RG727 from the line
            rg727_value = re.search(r'\bRG727\s*=\s*(\d+)', line)
            if rg727_value:
                rg727_value = rg727_value.group(1)
                #add to variables
                self.variables['RG727'] = rg727_value
                print(f"Channel {channel_number} RG727 = {rg727_value}")

        # Handle variable assignments
        '''
        ex:
        ;BROCHE 3 = FERMETURE PAR PRESSION (invalid syntax (<string>, line 1)) --> comment
        ;RG901 = 1  ; (RE)DEMARRAGE A L'OPERATION x - CANAL 1 (unterminated string literal (detected at line 1) (<string>, line 1))
        RG901 = 1  ; (RE)DEMARRAGE A L'OPERATION x - CANAL 1 (unterminated string literal (detected at line 1) (<string>, line 1))
        RG707=1         ; BRIS OUTIL 0=INACTIF 1=ACTIF
        RG720=0       ; ZERO PIECE BROCHE 4 + CORRIGER Z=0
        RG721=262.05+63.8 ; LONGUEUR MOYEN DE SERRAGE BROCHE 3/ORIGINE MACHINE
        RG722=0         ; SANS EFFET
        RG724=0        ; PROFONDEUR DE SERRAGE SUR BROCHE 3
        ; RG711=262.3+44.82  ;LONGUEUR MANDRIN + MORS S4
        RG711=309.3;
        RG712=3.5       ; LARGEUR TRONCONNAGE
        RG713=1369.9    ; POSITION DE TRAVAIL Z3
        RG714=RG711     ; ORIGINE G54
        RG715=RG713-RG721 ; ORIGINE G55   
        DEF REAL CURROP_2
        EXTERN DUMMY (INT)
        '''
        # Handle DEF REAL var
        match_def = re.match(r'DEF\s+REAL\s+([A-Z_][A-Z0-9_]*)', line)
        if match_def:
            var_name = match_def.group(1)
            self.variables[var_name] = 0
            #get the value of the variable
            value = re.search(r'([A-Z_][A-Z0-9_]*)', line)
            if value:
                value = value.group(1)
                self.variables[var_name] = self.variables.get(value, 0)
                print(f"Declared variable {var_name} with value {self.variables[var_name]}")
            else:
                print(f"Declared variable {var_name} with default 0")


            
        # Handle EXTERN VAR (TYPE)
        match_extern = re.match(r'EXTERN\s+([A-Z_][A-Z0-9_]*)\s*\(\s*[A-Z]+\s*\)', line)
        if match_extern:
            var_name = match_extern.group(1)
            self.variables[var_name] = 0
            #get the value of the variable
            value = re.search(r'([A-Z_][A-Z0-9_]*)', line)
            if value:
                value = value.group(1)
                self.variables[var_name] = self.variables.get(value, 0)
                print(f"Declared EXTERN variable {var_name} with value {self.variables[var_name]}")
            else:
                print(f"Declared EXTERN variable {var_name} with default 0")

        # Handle $-based parameter assignments
        dollar_param = re.match(r'^\s*(\$\w+\[.*?\])\s*=\s*([^\s;]+)', line)
        if dollar_param:
            param_name = dollar_param.group(1).strip()
            value_expr = dollar_param.group(2).strip()

            #remove $
            if param_name.startswith("$"):
                param_name = param_name[1:]

            
            # Try to resolve variable in value (like RG714)
            resolved_expr = re.sub(
                r"\b(\$?[A-Z]+\d+)\b",
                lambda m: str(self.variables.get(m.group(1), 0)),
                value_expr
            )
            try:
                value = eval(resolved_expr)
            except Exception as e:
                print(f"Failed to evaluate $ param: {param_name} = {resolved_expr} ({e})")
                value = None

            self.variables[param_name] = value
            print(f"Set parameter {param_name} = {value}")

        # Handle RGxxx assignments
        self.process_rg_assignments(line)

        # Handle def var assignment that is not RGxxx
        # Check if not RGxxx
        if re.search(r'RG\d{3}', line):
            # Skip this line
            pass
        else:
            match_def_assign = re.match(r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+)', line)
            if match_def_assign:
                var_name = match_def_assign.group(1)
                expr = match_def_assign.group(2).strip()
                expr_resolved = re.sub(r"(\$?[A-Z]+\d+)", lambda m: str(self.variables.get(m.group(1), 0)), expr)

                try:
                    value = eval(expr_resolved)
                    self.variables[var_name] = round(value, 5)
                    print(f"Set {var_name} = {expr_resolved} => {value}")
      
                except Exception as e:
                    print(f"Failed to evaluate: {var_name} = {expr_resolved} ({e})")
                    self.variables[var_name] = None
                    return
            

        # Handle conditional jumps
        if re.search(r'\bIF\b', line):
            condition_part = line.split("IF", 1)[1].strip()

            # Normalize operators for Python eval
            condition_part = (
                condition_part
                .replace("<>", "!=")
                .replace(" OR ", " or ")
                .replace(" AND ", " and ")
            )

            # Check for GOTOF
            if "GOTOF" in condition_part:
                condition_expr, target_label = condition_part.split("GOTOF", 1)
                condition_expr = condition_expr.strip()
                target_label = target_label.strip()

                try:
                    # Combine known variables
                    known_vars = {
                        "CHAN_NO": channel_number,
                        **self.variables
                    }


                    condition_expr = re.sub(r"\bNOT\b", "not", condition_expr, flags=re.IGNORECASE)
                    condition_expr = re.sub(r"\bAND\b", "and", condition_expr, flags=re.IGNORECASE)
                    condition_expr = re.sub(r"\bOR\b", "or", condition_expr, flags=re.IGNORECASE)


                    # Regex matches variables like CURROP_2, RG902, $RG707
                    condition_eval = re.sub(
                        r"(\$?[A-Z_][A-Z0-9_]*)",  # No \b to ensure $ is matched
                        lambda m: self.var_replacer(m, known_vars),
                        condition_expr
                    )

                    print(f"Evaluating condition: {condition_expr} → {condition_eval}")
                    result = eval(condition_eval)
                    print(f"Evaluated: {condition_eval} → {result}")

                    if result:
                        print(f"Condition is TRUE → Executing GOTOF to label {target_label}")
                        program_lines = self.channel_1 if channel_number == 1 else self.channel_2
                        label_line = next(
                            (i for i, l in enumerate(program_lines) if l.strip().startswith(f"{target_label}:")),
                            None
                        )

                        if label_line is not None:
                            if channel_number == 1:
                                self.current_step_1 = label_line - 1
                            else:
                                self.current_step_2 = label_line - 1
                            print(f"Channel {channel_number} jumped to line {label_line + 1} ({target_label})")
                        else:
                            print(f"Label {target_label} not found in channel {channel_number}")
                    else:
                        print("Condition is FALSE → Continuing to next step")

                except Exception as e:
                    print(f"Failed to evaluate GOTOF condition: {line} ({e})")

            else:
                # Handle IF without GOTOF (block control)
                condition_expr = condition_part.strip()

                #strip $
                if condition_expr.startswith("$"):
                    condition_expr = condition_expr[1:]

                # Normalize shorthand like "IF VAR" → "IF VAR != 0"
                if re.match(r'^\$?[A-Z_][A-Z0-9_]*$', condition_expr):
                    condition_expr += ' == True'

                try:
                    known_vars = {
                        "CHAN_NO": channel_number,
                        **self.variables
                    }

                    condition_eval = re.sub(
                        r"\b(\$?[A-Z_][A-Z0-9_]*)\b",
                        lambda match: self.var_replacer(match, known_vars),
                        condition_expr
                    )

                    result = eval(condition_eval)
                    print(f"Evaluating IF block condition: {condition_expr} → {condition_eval} → {result}")

                    if not result:
                        step_attr = "current_step_1" if channel_number == 1 else "current_step_2"
                        steps = self.channel_1 if channel_number == 1 else self.channel_2

                        curr = getattr(self, step_attr)
                        while curr < len(steps):
                            if "ENDIF" in steps[curr]:
                                break
                            curr += 1
                        setattr(self, step_attr, curr)
                    else:
                        # If condition is true, just continue to the next step
                        print(f"Condition is TRUE → Continuing to next step")
                        pass
                        '''if channel_number == 1:
                            self.current_step_1 += 1
                        else:
                            self.current_step_2 += 1'''

                except Exception as e:
                    print(f"Failed to evaluate IF block: {line} ({e})")
                    # Even if condition is invalid, treat it as false and skip to ENDIF
                    step_attr = "current_step_1" if channel_number == 1 else "current_step_2"
                    steps = self.channel_1 if channel_number == 1 else self.channel_2

                    curr = getattr(self, step_attr)
                    while curr < len(steps):
                        if "ENDIF" in steps[curr]:
                            break
                        curr += 1
                    setattr(self, step_attr, curr)


                
        # Handle M0 and M1 commands
        if re.search(r'\bM[01]\b', line):
            if self.state == "RUN":
                self.state = "M0"
                self.ch1_run = False                
                self.ch2_run = False
                print(f"Channel {channel_number} paused at step {current_step + 1}.")
                return
            elif self.state == "M0":
                self.state = "RUN"
                print(f"Channel {channel_number} resumed at step {current_step + 1}.")
                



        #Handle M30 ( end of program ) ex: NN9999: M30

        if re.search(r'M30\b', line):
            if channel_number == 1:
                self.current_step_1 = len(self.channel_1)
                self.ch1_run = False
            else:
                self.current_step_2 = len(self.channel_2)
                self.ch2_run = False
            print(f"Channel {channel_number} ended program execution at step {current_step + 1}.")
            return


        # Handle return from subprogram (M17)
        if "M17" in line:
            if stack:
                if channel_number == 1:
                    self.channel_1, self.current_step_1 = stack.pop()
                    self.current_step_1 += 1
                else:
                    self.channel_2, self.current_step_2 = stack.pop()
                    self.current_step_2 += 1
                print(f"Channel {channel_number} returned from subprogram.")
                return

        # Process WAITM commands
        if "WAITM(" in line:
            if channel_number == 1 and self.ch1_run:
                print(f"Channel {channel_number} is waiting at step {current_step + 1}.")
            elif channel_number == 2 and self.ch2_run:  
                print(f"Channel {channel_number} is waiting at step {current_step + 1}.")

            if channel_number == 1:
                self.ch1_run = False
            else:
                self.ch2_run = False
                

        # If both channels are waiting, check for synchronization
        if self.ch1_run == False and self.ch2_run == False:
            conteudo_ch1 = self.extrair_conteudo_waitm(self.channel_1[self.current_step_1])
            conteudo_ch2 = self.extrair_conteudo_waitm(self.channel_2[self.current_step_2])
            
            if conteudo_ch1 == conteudo_ch2:
                self.ch1_run = self.ch2_run = True
                print(f"Both channels are synchronized at step {self.current_step_1 + 1}.")
                self.current_step_1 += 1
                self.current_step_2 += 1

        else:
            # Allow the running channel to proceed
            if channel_number == 1 and self.ch1_run and self.current_step_1 < len(self.channel_1):
                self.current_step_1 += 1
            if channel_number == 2 and self.ch2_run and self.current_step_2 < len(self.channel_2):
                self.current_step_2 += 1


    def process_rg_assignments(self, line):
        """Process RGxxx assignments in the line."""
        # Handle RGxxx assignments
        match = re.search(r'RG(\d{3})\s*=\s*([^;]+)', line)
        if match:
            var_name = f"RG{match.group(1)}"
            expr = match.group(2).strip()
            expr_resolved = re.sub(r"(\$?[A-Z]+\d+)", lambda m: str(self.variables.get(m.group(1), 0)), expr)

            try:
                value = eval(expr_resolved)
                self.variables[var_name] = round(value, 5)
                print(f"Set {var_name} = {expr_resolved} => {value}")
                return value
            except Exception as e:
                print(f"Failed to evaluate: {var_name} = {expr_resolved} ({e})")
                self.variables[var_name] = None
            

    def _parse_goto(self, line):
        """Helper function to extract the target line from a GOTO command."""
        if "GOTO" in line:
            parts = line.split()
            if len(parts) > 1:
                try:
                    return int(parts[1])  # Return the target line number
                except ValueError:
                    pass
        return None

    def _extract_subprogram_call(self, line):
        """Finds Lxxxx subprogram call in a line like 'N60 L1001 ;Comment'."""
        if line.startswith(";"):
            return None
        match = re.search(r'\bL(\d{4})\b', line)
        if match:
            return f"L{match.group(1)}"
        match = re.search(r'\bL(\d{4})\s*:', line)
        if match:
            return f"L{match.group(1)}"
        return None

    def open_subprogram(self, subprogram_name, channel):
        """Push current state, load a subprogram, and replace channel content."""
        try:
            filename = f"{subprogram_name}.SPF"
            subprogram_path = os.path.join(self.directory, filename)

            with open(subprogram_path, 'r') as file:
                subprogram_content = self._parse_lines(file.read().splitlines())

                if channel == 1:
                    self.ch1_stack.append((self.channel_1, self.current_step_1))  # Push current state
                    self.channel_1 = subprogram_content
                    self.current_step_1 = 0
                elif channel == 2:
                    self.ch2_stack.append((self.channel_2, self.current_step_2))
                    self.channel_2 = subprogram_content
                    self.current_step_2 = 0

                return True
        except FileNotFoundError:
            print(f"Subprogram {subprogram_name}.SPF not found.")
        except Exception as e:
            print(f"Error loading subprogram {subprogram_name}: {e}")
        return False

    def open_machine_program(self, subprogram_name, channel):
        """Load a machine subprogram, and replace channel content."""
        try:
            filename = f"N_L{subprogram_name}_SPF.txt"
            subprogram_path = os.path.join(self.directory, "machine", filename)
            
            with open(subprogram_path, 'r') as file:
                subprogram_content = self._parse_lines(file.read().splitlines())

                if channel == 1:
                    self.ch1_stack.append((self.channel_1, self.current_step_1))  # Push current state
                    self.channel_1 = subprogram_content
                    self.current_step_1 = 0
                elif channel == 2:
                    self.ch2_stack.append((self.channel_2, self.current_step_2))
                    self.channel_2 = subprogram_content
                    self.current_step_2 = 0

                return True
        except FileNotFoundError:
            print(f"Machine program {subprogram_name}.SPF not found.")
        except Exception as e:
            print(f"Error loading machine program {subprogram_name}: {e}")
        return False
