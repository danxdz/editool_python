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
                parsed_lines.append(clean_line)
                continue

            if clean_line.startswith("IF "):
                if "GOTOF" in clean_line:
                    # Siemens-style conditional jump
                    condition_part, label = clean_line[3:].split("GOTOF")
                    condition_expr = condition_part.strip().replace("<>", "!=")
                    target_label = label.strip()

                    try:
                        condition_expr = condition_expr.replace("<>", "!=").replace(" OR ", " or ").replace(" AND ", " and ").replace(" NOT ", " not ")
                        condition_eval = re.sub(r"(\$?[A-Z]+\d+|\b[A-Z_]+\d+\b)", lambda m: str(self.variables.get(m.group(1), 0)), condition_expr)
                        result = eval(condition_eval)
                        if not result:
                            print(f"Jumping to label {target_label} (condition {condition_expr} was False)")
                            self._jump_to_label = target_label  # implement this behavior
                    except Exception as e:
                        print(f"Failed to eval conditional jump: {clean_line} ({e})")
                    continue

            if clean_line.startswith("ENDIF"):
                if self.condition_stack:
                    self.condition_stack.pop()
                continue

            if False in self.condition_stack:
                continue  # skip lines inside an unmet IF

            code_part = clean_line.split(";")[0].strip()

            match = re.match(r"^(?P<var>\$?[A-Z]+\d+)\s*=\s*(?P<expr>.+)$", code_part)
            if match:
                var = match.group("var")
                expr = match.group("expr")
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

    def run_program(self):
        """Runs both channels until completion."""
        print("Starting program execution...")
        while self.current_step_1 < len(self.channel_1) or self.current_step_2 < len(self.channel_2):
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

    def step_execution(self):
        """Simulate stepping through the program for both channels, independently."""
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
        
        # Handle machine program calls (Lxxx)
        if "PROC" not in line and "def" not in line and "L" in line:
            l_call = re.search(r'\bL(\d{3})\b', line)
            if l_call:
                l_number = l_call.group(1)
                print(f"Channel {channel_number} calling machine program L{l_number}.")
                if self.open_machine_program(l_number, channel=channel_number):
                    print(f"Channel {channel_number} is now executing L{l_number}.SPF")
                return
            
        # Handle M0 and M1 commands
        if "M0" in line or "M1" in line:
            if channel_number == 1:
                self.ch1_run = False
            else:
                self.ch2_run = False
            print(f"Channel {channel_number} paused at step {current_step + 1}.")
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
