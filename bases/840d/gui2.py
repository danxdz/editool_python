import tkinter as tk
from tkinter import scrolledtext, messagebox, font
from tkinter import filedialog  # For file selection dialog
from program_handler import ProgramHandler
from channel_state import ChannelState

import time

import threading

class NC_Debugger_GUI:
    def __init__(self, master, program_handler: ProgramHandler, channel_state: ChannelState = None):
        """Initialize the GUI components and layout."""
        self.master = master
        self.running = False
        self.thread = None
        self.program_handler = program_handler
        self.channel_state = channel_state if channel_state else ChannelState(1)  # Default to channel 1
        self.mono_font = font.Font(family="Courier New", size=10)
        self.status_font = font.Font(family="Segoe UI", size=9)
        self.setup_gui()

    def setup_gui(self):
        top = tk.Frame(self.master, pady=5)
        top.pack(fill=tk.X, padx=5)

        # Interface components
        self.call_entry = tk.Entry(top, width=60)
        self.call_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.load_button = tk.Button(top, text="Load", command=self.load_program, width=8)
        self.load_button.pack(side=tk.LEFT, padx=2)
        
        self.play_button = tk.Button(top, text="▶️ Play", command=self.run_program, state=tk.DISABLED, width=8)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        self.step_button = tk.Button(top, text="Step", command=self.step_execution, state=tk.DISABLED, width=8)
        self.step_button.pack(side=tk.LEFT, padx=2)
        
        self.reset_button = tk.Button(top, text="Reset", command=self.reset_simulation, state=tk.DISABLED, width=8)
        self.reset_button.pack(side=tk.LEFT, padx=2)
        
        # Output Areas
        mpane = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bd=2)
        mpane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame for Channel 1
        cframe_1 = tk.LabelFrame(mpane, text="Channel 1", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.channel_1_text = scrolledtext.ScrolledText(cframe_1, wrap=tk.NONE, font=self.mono_font, height=20, width=60)
        self.channel_1_text.pack(fill=tk.BOTH, expand=True)
        self.channel_1_text.config(state=tk.DISABLED)
        mpane.add(cframe_1, stretch="always")
        self.stack_label_1 = tk.Label(cframe_1, text="Stack: []", anchor="w", font=("Segoe UI", 8))
        self.stack_label_1.pack(fill=tk.X)

        
        # Center frame for Channel 2
        cframe_2 = tk.LabelFrame(mpane, text="Channel 2", bd=1, relief=tk.SUNKEN, padx=2, pady=2)
        self.channel_2_text = scrolledtext.ScrolledText(cframe_2, wrap=tk.NONE, font=self.mono_font, height=20, width=60)
        self.channel_2_text.pack(fill=tk.BOTH, expand=True)
        self.channel_2_text.config(state=tk.DISABLED)
        mpane.add(cframe_2, stretch="always")
        self.stack_label_2 = tk.Label(cframe_2, text="Stack: []", anchor="w", font=("Segoe UI", 8))
        self.stack_label_2.pack(fill=tk.X)

        # Right frame for Variables
        var_frame = tk.LabelFrame(mpane, text="Variables", bd=1, relief=tk.SUNKEN, padx=2, pady=2)    
        var_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.var_listbox = tk.Listbox(var_frame, font=self.mono_font, width=25)
        self.var_listbox.pack(fill=tk.BOTH, expand=True)

        mpane.add(var_frame, stretch="always")
        # Status display
        self.status_label = tk.Label(self.master, text="Status: Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.status_font)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    def update_variable_listbox(self):
        """Update the variable listbox with current variable values."""
        self.var_listbox.delete(0, tk.END)
        for var, val in sorted(self.program_handler.variables.items()):
            self.var_listbox.insert(tk.END, f"{var} = {val}")


    def run_program(self):
        if not self.running:
            # Start running
            self.running = True
            self.play_button.config(text="⏸️ Pause")
            self.thread = threading.Thread(target=self._run_program_loop)
            self.thread.daemon = True
            self.thread.start()
        else:
            # Pause execution
            self.running = False
            self.play_button.config(text="▶️ Play")


    def _run_program_loop(self):
        self.update_status("Running...")
        while self.running and (
            self.program_handler.current_step_1 < len(self.program_handler.channel_1)
            or self.program_handler.current_step_2 < len(self.program_handler.channel_2)
        ):
            self.program_handler.step_execution()

            self.master.after(0, self.scroll_and_highlight)
            self.master.after(0, lambda: self.stack_label_1.config(
                text=f"Stack: {[line[0][0] for line in self.program_handler.ch1_stack]}"))
            self.master.after(0, lambda: self.stack_label_2.config(
                text=f"Stack: {[line[0][0] for line in self.program_handler.ch2_stack]}"))
            self.master.after(0, self.update_variable_listbox)

            time.sleep(0.01)  # Adjust the sleep time as needed

        self.master.after(0, self.update_status, "Program execution completed.")
        self.master.after(0, lambda: self.play_button.config(text="▶️ Play"))
        self.running = False



    def load_program(self):
        # Open file selection dialog for .job files
        file_name = filedialog.askopenfilename(title="Select a .job File", filetypes=[("Job Files", "*.job"), ("All Files", "*.*")])
        
        if not file_name:
            messagebox.showerror("Error", "No file selected!")
            return

        self.program_handler.load_program(file_name)
        self.update_ui_on_program_load()
        self.display_channel_content()

    def update_ui_on_program_load(self):
        self.step_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.DISABLED)

        self.status_label.config(text="Program loaded. Ready for execution.")

    def display_channel_content(self):
        """Display the content of both channels in the text areas."""
        if not self.program_handler.channel_1 or not self.program_handler.channel_2:
            messagebox.showerror("Error", "Program files are empty or not loaded correctly.")
            return
        
        # Join lines without comments
        channel_1_content = "\n".join(self.program_handler.channel_1)
        channel_2_content = "\n".join(self.program_handler.channel_2)
        
        # Display the content
        self.channel_1_text.config(state=tk.NORMAL)
        self.channel_1_text.delete(1.0, tk.END)
        self.channel_1_text.insert(tk.END, channel_1_content)
        self.channel_1_text.config(state=tk.DISABLED)
        
        self.channel_2_text.config(state=tk.NORMAL)
        self.channel_2_text.delete(1.0, tk.END)
        self.channel_2_text.insert(tk.END, channel_2_content)
        self.channel_2_text.config(state=tk.DISABLED)


    def step_execution(self):
        self.program_handler.step_execution()
        self.update_status("Stepping through program...")
        self.display_channel_content()  # Refresh entire content!
        self.scroll_and_highlight()
        self.stack_label_1.config(text=f"Stack: {[line[0][0] for line in self.program_handler.ch1_stack]}")
        self.stack_label_2.config(text=f"Stack: {[line[0][0] for line in self.program_handler.ch2_stack]}")
        self.update_variable_listbox()




    def scroll_and_highlight(self):
        """Scroll to and highlight the current line in both text widgets."""
        current_line_1 = self.program_handler.current_step_1 + 1
        current_line_2 = self.program_handler.current_step_2 + 1

        # Clear old highlights
        self.channel_1_text.tag_remove("highlight", "1.0", tk.END)
        self.channel_2_text.tag_remove("highlight", "1.0", tk.END)

        # Highlight current lines
        self.channel_1_text.tag_add("highlight", f"{current_line_1}.0", f"{current_line_1}.end")
        self.channel_2_text.tag_add("highlight", f"{current_line_2}.0", f"{current_line_2}.end")

        self.channel_1_text.tag_configure("highlight", background="yellow")
        self.channel_2_text.tag_configure("highlight", background="yellow")

        # Scroll the view to center around the current line
        self.channel_1_text.see(f"{current_line_1}.0")
        self.channel_2_text.see(f"{current_line_2}.0")


    def refresh_textboxes(self):
        """Reload both channel text areas with current program lines."""
        # Update Channel 1
        self.channel_1_text.config(state=tk.NORMAL)
        self.channel_1_text.delete(1.0, tk.END)
        self.channel_1_text.insert(tk.END, "\n".join(self.program_handler.channel_1))
        self.channel_1_text.config(state=tk.DISABLED)

        # Update Channel 2
        self.channel_2_text.config(state=tk.NORMAL)
        self.channel_2_text.delete(1.0, tk.END)
        self.channel_2_text.insert(tk.END, "\n".join(self.program_handler.channel_2))
        self.channel_2_text.config(state=tk.DISABLED)


    def highlight_current_line(self, line_channel_1, line_channel_2):
        """Highlight the current line in both channels and keep them in sync."""
        current_line_1 = self.program_handler.current_step_1 + 1  # Channel 1 line number
        current_line_2 = self.program_handler.current_step_2 + 1  # Channel 2 line number

        # Ensure the text widgets show the current line properly
        self.channel_1_text.yview_pickplace(f"{current_line_1}.0")
        self.channel_2_text.yview_pickplace(f"{current_line_2}.0")

        # Highlight the current line
        self.channel_1_text.tag_add("highlight", f"{current_line_1}.0", f"{current_line_1}.end")
        self.channel_2_text.tag_add("highlight", f"{current_line_2}.0", f"{current_line_2}.end")
        self.channel_1_text.tag_configure("highlight", background="yellow")
        self.channel_2_text.tag_configure("highlight", background="yellow")

    def reset_simulation(self):
        self.program_handler.reset_simulation()
        self.update_status("Simulation reset.")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def reset_simulation(self):
        """Resets the simulation and reloads the main programs in both channels."""
        self.program_handler.reset_simulation()

        # Set text areas to the main programs
        self.channel_1_text.delete("1.0", tk.END)
        self.channel_1_text.insert(tk.END, self.program_handler.loaded_program1)

        self.channel_2_text.delete("1.0", tk.END)
        self.channel_2_text.insert(tk.END, self.program_handler.loaded_program2)

        # Reprocess and highlight new content
        self.refresh_textboxes()
        self.scroll_and_highlight()



        # Reset stack displays
        self.stack_label_1.config(text="Stack: []")
        self.stack_label_2.config(text="Stack: []")

        # Reset variable list
        self.update_variable_listbox()

        # Remove highlights
        self.channel_1_text.tag_remove("highlight", "1.0", tk.END)
        self.channel_2_text.tag_remove("highlight", "1.0", tk.END)

        # Reactivate buttons
        self.step_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)  # ✅ allow loading a new program

        self.update_status("Simulation reset to main programs.")

        #stop the current thread if running
        if self.running:
            self.running = False
            if self.thread.is_alive():
                self.thread.join()
    
    def update_status(self, message):
        """Update the status label with the provided message."""
        self.status_label.config(text=f"Status: {message}")
    def update_variable_listbox(self):
        self.var_listbox.delete(0, tk.END)
        for var, val in sorted(self.program_handler.variables.items()):
            self.var_listbox.insert(tk.END, f"{var} = {val}")
