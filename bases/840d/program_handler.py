import os
import re

BASE_PATH = "nc_programs"
class ProgramHandler:
    def __init__(self):
        self.channel_1 = []
        self.channel_2 = []
        self.current_step_1 = 0  # Track the current step for Channel 1
        self.current_step_2 = 0  # Track the current step for Channel 2
        self.channel_1_file = ""
        self.channel_2_file = ""
        self.ch1_run = True  # Flag to indicate if Channel 1 is running
        self.ch2_run = True  # Flag to indicate if Channel 2 is running
        self.directory = os.path.dirname(__file__)
        self.ch1_stack = []  # stack of (file, step, content)
        self.ch2_stack = []
        self.variables = {}  # Stores RGxxx and $vars
        self.condition_stack = []  # For handling IF conditions





    def load_program(self, job_file):
        """Load the .job file and extract the files for Channel 1 and Channel 2."""
        try:
            self.directory = os.path.dirname(job_file)

            with open(job_file, 'r') as file:
                program_data = file.read().splitlines()

                for line in program_data:
                    if "SELECT" in line:
                        parts = line.split()
                        if len(parts) > 1 and parts[1].endswith(".MPF"):
                            if "CH=1" in line:
                                self.channel_1_file = parts[1]
                            elif "CH=2" in line:
                                self.channel_2_file = parts[1]

            # Load content from the MPF files for both channels
            self.load_channel_content(self.directory)

        except FileNotFoundError:
            print(f"Error: File {job_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def load_channel_content(self, directory):
        """Load the contents of Channel 1 and Channel 2 files."""
        try:
            # Load Channel 1 content if available
            if self.channel_1_file:
                channel_1_path = os.path.join(directory, self.channel_1_file)
                if os.path.exists(channel_1_path):
                    with open(channel_1_path, 'r') as file:
                        self.channel_1 = self._parse_lines(file.read().splitlines())
                else:
                    self.channel_1 = [f"Error: {self.channel_1_file} not found."]
            else:
                self.channel_1 = ["Error: Channel 1 file not specified."]

            # Load Channel 2 content if available
            if self.channel_2_file:
                channel_2_path = os.path.join(directory, self.channel_2_file)
                if os.path.exists(channel_2_path):
                    with open(channel_2_path, 'r') as file:
                        self.channel_2 = self._parse_lines(file.read().splitlines())
                else:
                    self.channel_2 = [f"Error: {self.channel_2_file} not found."]
            else:
                self.channel_2 = ["Error: Channel 2 file not specified."]
                
        except Exception as e:
            print(f"An error occurred while loading files: {e}")



    def _parse_lines(self, lines):
        parsed_lines = []
        self.condition_stack = []  # Reset condition block

        for line in lines:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith(";;;;"):  # Skip empty lines and comments
                continue  # Skip full comments or empty lines

            # Handle IF condition
            if clean_line.startswith("IF "):
                if "GOTOF" in clean_line:
                    # Siemens-style conditional jump
                    condition_part, label = clean_line[3:].split("GOTOF")
                    condition_expr = condition_part.strip().replace("<>", "!=")
                    target_label = label.strip()

                    try:
                        # Replace RG/$ vars in condition
                        condition_eval = re.sub(r"(\$?[A-Z]+\d+)", lambda m: str(self.variables.get(m.group(1), 0)), condition_expr)
                        result = eval(condition_eval)
                        if not result:
                            print(f"Jumping to label {target_label} (condition {condition_expr} was False)")
                            # You may want to store a jump signal, or skip lines until label
                            self._jump_to_label = target_label  # implement this behavior
                    except Exception as e:
                        print(f"Failed to eval conditional jump: {clean_line} ({e})")
                    continue

            # Handle ENDIF (optional for future nested conditions)
            if clean_line.startswith("ENDIF"):
                if self.condition_stack:
                    self.condition_stack.pop()
                continue

            # Check if we're inside a false IF block
            if False in self.condition_stack:
                continue  # skip lines inside an unmet IF

            # Remove inline comments
            code_part = clean_line.split(";")[0].strip()

            # Handle assignments
            match = re.match(r"^(?P<var>\$?[A-Z]+\d+)\s*=\s*(?P<expr>.+)$", code_part)
            if match:
                var = match.group("var")
                expr = match.group("expr")

                # Replace variables in the expression
                expr_resolved = re.sub(r"(\$?[A-Z]+\d+)", lambda m: str(self.variables.get(m.group(1), 0)), expr)

                try:
                    value = eval(expr_resolved)
                    self.variables[var] = round(value, 5)
                    print(f"Set {var} = {expr_resolved} => {value}")
                except Exception as e:
                    print(f"Failed to evaluate: {var} = {expr_resolved} ({e})")
                    self.variables[var] = None

            parsed_lines.append(clean_line)

        return parsed_lines

    def _evaluate_condition(self, condition_expr):
        try:
            # Replace `<>` with `!=` to make it valid Python syntax
            condition_expr = condition_expr.replace("<>", "!=")


            # Replace variables in the condition (both $vars and RGxx vars)
            condition_expr = re.sub(
                r"(\$?[A-Z]+\d+)", 
                lambda m: str(self.variables.get(m.group(1), 0)), 
                condition_expr
            )

            # Now evaluate the condition with the corrected syntax
            # Using locals() or globals() to ensure the variables are accessible
            return bool(eval(condition_expr, {}, self.variables))
        except Exception as e:
            print(f"Condition eval failed: {condition_expr} ({e})")
            return False




    def _extract_subprogram_call(self, line):
        """Finds Lxxxx subprogram call in a line like 'N60 L1001 ;Comment'."""
        match = re.search(r'\bL(\d{4})\b', line)
        if match:
            return f"L{match.group(1)}"
        
        # Check for subprogram calls in the form of Lxxx : machine code #line = N55 L708  ;Description
        # This is a more specific case where Lxxx is followed by a colon and some other text
        match = re.search(r'\bL(\d{4})\s*:', line) # d
        if match:
            return f"L{match.group(1)}"
        
        return None
    
    def run_program(self):
        """Runs both channels until completion."""
        print("Starting program execution...")
        while self.current_step_1 < len(self.channel_1) or self.current_step_2 < len(self.channel_2):
            self.step_execution()
        print("Program execution completed.")




    def step_execution(self):
        """Simulate stepping through the program for both channels, independently."""
        # Process steps for both channels
        self.process_channel_step(1)
        self.process_channel_step(2)

    def process_channel_step(self, channel_number):
        """Process a single step for the given channel (1 or 2)."""
        if channel_number == 1:
            line = self.channel_1[self.current_step_1]
            current_step = self.current_step_1
            stack = self.ch1_stack
            wait_flag = self.ch1_run
        else:
            line = self.channel_2[self.current_step_2]
            current_step = self.current_step_2
            stack = self.ch2_stack
            wait_flag = self.ch2_run

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
        
        # Handle machine program calls (Lxxx) L708 , L700
        # Check if the line start not with PROC
        if "PROC" not in line:
            if "def" not in line:
                if "L" in line:                
                    l_call = re.search(r'\bL(\d{3})\b', line)
                    if l_call:
                        l_number = l_call.group(1)
                        print(f"Channel {channel_number} calling machine program L{l_number}.")
                        if self.open_machine_program(l_number, channel=channel_number):
                            print(f"Channel {channel_number} is now executing L{l_number}.SPF")
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
            if self.channel_1[self.current_step_1] == self.channel_2[self.current_step_2]:
                self.ch1_run = self.ch2_run = True
                print(f"Both channels are synchronized at step {self.current_step_1 + 1}.")
                self.current_step_1 += 1
                self.current_step_2 += 1
            return

        # Allow the running channel to proceed
        if channel_number == 1 and self.ch1_run:
            self.current_step_1 += 1
        elif channel_number == 2 and self.ch2_run:
            self.current_step_2 += 1

                

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

    def get_current_lines(self):
        """Get the current line from both channels."""
        line_channel_1 = self.channel_1[self.current_step_1] if self.current_step_1 < len(self.channel_1) else "End of Channel 1"
        line_channel_2 = self.channel_2[self.current_step_2] if self.current_step_2 < len(self.channel_2) else "End of Channel 2"
        return line_channel_1, line_channel_2

    def reset_simulation(self):
        """Reset the simulation state."""
        self.current_step_1 = 0
        self.current_step_2 = 0

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
        """Push current state, load a subprogram, and replace channel content."""
        try:
            filename = f"N_L{subprogram_name}_SPF.txt"
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