class ChannelSimulation:
    def __init__(self, channel_number):
        self.channel_number = channel_number
        self.program = []
        self.current_line = 0
    
    def load_program(self, program_lines):
        """Load the program lines for the simulation."""
        self.program = program_lines
        self.current_line = 0  # Reset current line to start from the beginning
    
    def execute(self):
        """Execute the full program in the current channel."""
        if not self.program:
            print(f"Channel {self.channel_number} has no program loaded.")
            return
        
        print(f"Executing full program on Channel {self.channel_number}:")
        while self.current_line < len(self.program):
            line = self.program[self.current_line]
            print(f"Executing on Channel {self.channel_number}: {line}")
            
            if self._is_goto(line):
                self.handle_goto(line)
            elif self._is_wait(line):
                self.handle_wait(line)
            else:
                # Handle normal execution
                self.current_line += 1
            
            # Simulate pause or delay as needed
            # You could insert a time delay for stepping through instructions if desired
    
    def step(self):
        """Step through one line of the program at a time."""
        if self.current_line < len(self.program):
            line = self.program[self.current_line]
            print(f"Stepping through on Channel {self.channel_number}: {line}")
            
            if self._is_goto(line):
                self.handle_goto(line)
            elif self._is_wait(line):
                self.handle_wait(line)
            else:
                self.current_line += 1
            return False  # Not done yet, more steps to execute
        else:
            print(f"Channel {self.channel_number} has reached the end of the program.")
            return True  # Finished all steps
    
    def reset(self):
        """Reset the simulation to the start."""
        self.current_line = 0
        print(f"Channel {self.channel_number} simulation has been reset.")
    
    def is_done(self):
        """Check if the program has finished execution."""
        return self.current_line >= len(self.program)
    
    def _is_goto(self, line):
        """Check if the line contains a GOTO command."""
        return line.strip().upper().startswith("GOTO")
    
    def _is_wait(self, line):
        """Check if the line contains a WAIT command."""
        return line.strip().upper().startswith("WAIT")
    
    def handle_goto(self, line):
        """Handle GOTO command, jump to the specified line."""
        match = re.match(r"GOTO\s+(\d+)", line, re.IGNORECASE)
        if match:
            target_line = int(match.group(1)) - 1  # Convert to 0-based index
            print(f"Channel {self.channel_number}: Jumping to line {target_line + 1}")
            self.current_line = target_line
        else:
            print(f"Channel {self.channel_number}: Invalid GOTO command.")
            self.current_line += 1  # Skip invalid command
    
    def handle_wait(self, line):
        """Handle WAIT command. In a real scenario, you would wait for a condition."""
        print(f"Channel {self.channel_number}: Waiting (simulated for now).")
        # Here, you could add actual waiting logic, like waiting for user input, time, or other conditions.
        self.current_line += 1  # In this simplified version, just move to the next line after "waiting"
