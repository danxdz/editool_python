import re

class ChannelState:
    def __init__(self, number):
        self.number = number
        self.lines = []            # Loaded steps or subprogram lines
        self.current_step = 0
        self.stack = []
        self.run = True            # True = running, False = waiting
        self.subprograms = {}      # Dictionary to hold subprograms
        self.subprograms_loaded = False
        self.subprogram_name = None
        self.subprogram_line = None
        self.subprogram_line_number = None
        self.channels = {1: self, 2: self}  # Initializing channels (self for both)
        

    def current_line(self):
        if 0 <= self.current_step < len(self.lines):
            return self.lines[self.current_step]
        return None

    

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
    
    def step_execution(self):
        """Simulate stepping through the program for both channels, independently."""
        # Process steps for both channels
        self.process_channel_step(1)
        self.process_channel_step(2)

    def _extract_subprogram_call(self, line):
        """Finds Lxxxx subprogram call in a line like 'N60 L1001 ;Comment'."""
        match = re.search(r'\bL(\d{4})\b', line)
        if match:
            return f"L{match.group(1)}"
        return None
    
    def process_channel_step(self, channel_number):
        channel = self.channels[channel_number]

        line = channel.current_line()
        if not line:

            return  # No line to process

        # --- Handle GOTO ---
        if "GOTO" in line:
            target_line = self._parse_goto(line)
            if target_line is not None:
                channel.current_step = target_line - 1
                print(f"Channel {channel_number} GOTO to line {target_line}")
            return

        # --- Handle subprogram ---
        subprogram = self._extract_subprogram_call(line)
        if subprogram:
            print(f"Channel {channel_number} jumping to subprogram {subprogram}")
            channel.current_step += 1
            if self.open_subprogram(subprogram, channel=channel_number):
                print(f"Channel {channel_number} is now executing {subprogram}.SPF")
            return

        # --- Return from subprogram (M17) ---
        if "M17" in line:
            if channel.stack:
                channel.lines, channel.current_step = channel.stack.pop()
                channel.current_step += 1
                print(f"Channel {channel_number} returned from subprogram.")
            return

        # --- WAITM sync ---
        if "WAITM(" in line:
            print(f"Channel {channel_number} is waiting at step {channel.current_step + 1}.")
            channel.run = False

        # --- Check sync ---
        ch1 = self.channels[1]
        ch2 = self.channels[2]

        if not ch1.run and not ch2.run:
            if ch1.current_line() == ch2.current_line():
                print(f"Both channels synchronized at step {ch1.current_step + 1}")
                ch1.run = ch2.run = True
                ch1.current_step += 1
                ch2.current_step += 1
            return

        # --- Advance if running ---
        if channel.run:
            channel.current_step += 1
