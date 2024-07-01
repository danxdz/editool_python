import tkinter as tk
from tkinter import ttk
import bcrypt
import itertools
import string
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# Ensure the correct start method for multiprocessing
multiprocessing.set_start_method("spawn", force=True)

# Hashes to check
hashes = [
    b"$2a$11$S4KoyLVmEt8YTHoTytyn6u/iduGgBpH0KeGHRpP8FdlIrX5e8.qoG", # 123
    b"$2a$11$P1D5Bbp768zRE/noZzWrnebEJ9WOFQEKHfX0WBouq8u6Gef5wzqw.", # 10
    b"$2a$11$nz83oKYLgiBHdgTWt2p2FunHJxf1yrXh1qgmfnW7FjdHCVGfya5AC", # 1
    b"$2a$11$4GY/tpQZbI/R0J74avlGKus1P7sTQx/ET1GFsuAO9pj54wRrpQx1y", # 01
    b"$2a$11$OBQwmFoFtbTC9c5Tj6C0JO6f/jF51y411/HzaTiH2NVmnRClMOwve", # 0
    b"$2a$11$LOxar32P0hBPMaGO0hrfEu9GKlT4QWFjBxDezhQW41tVQqxYuscaK"  # TopSolid7
]

# Characters to include: digits and letters (both uppercase and lowercase)
default_characters = string.ascii_letters + string.digits

def check_combination(hash_value, combination):
    if bcrypt.checkpw(combination, hash_value):
        return combination.decode('utf-8')
    return None

def generate_combinations(characters, max_length, require_digits, require_letters, start_with):
    # Modify 'characters' based on user inputs
    if not require_digits:
        characters = [c for c in characters if c not in string.digits]
    if not require_letters:
        characters = [c for c in characters if c not in string.ascii_letters]
    if start_with:
        characters = list(start_with) + characters

    # Generate combinations
    for length in range(1, max_length + 1):
        for combo in itertools.product(characters, repeat=length):
            yield ''.join(combo).encode('utf-8')

def decrypt_hash(progress_queue, hash_value, max_length, require_digits, require_letters, start_with):
    combinations = list(generate_combinations(default_characters, max_length, require_digits, require_letters, start_with))
    total_combinations = len(combinations)

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = {executor.submit(check_combination, hash_value, combination): combination for combination in combinations}

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            progress_queue.put((i + 1, total_combinations, result))
            if result:
                executor.shutdown(wait=False, cancel_futures=True)
                return

class HashDecryptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hash Decryptor")

        # Variables
        self.hash_var = tk.StringVar()
        self.max_length_var = tk.IntVar(value=3)  # Default maximum length set to 3
        self.require_digits_var = tk.BooleanVar()
        self.require_letters_var = tk.BooleanVar()
        self.start_with_var = tk.StringVar()

        # Initialize UI
        self.create_widgets()
        self.setup_layout()

        # Progress queue
        self.progress_queue = multiprocessing.Queue()

    def create_widgets(self):
        # Labels and Entries
        ttk.Label(self.root, text="Hash to decrypt:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hash_combobox = ttk.Combobox(self.root, textvariable=self.hash_var, values=[hash.decode() for hash in hashes], width=50)
        self.hash_combobox.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        ttk.Label(self.root, text="Maximum length:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(self.root, from_=1, to=20, textvariable=self.max_length_var, width=5).grid(row=1, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Checkbutton(self.root, text="Require digits", variable=self.require_digits_var).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(self.root, text="Require letters", variable=self.require_letters_var).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.root, text="Start with:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.start_with_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky="we")
        
        # Start Button
        ttk.Button(self.root, text="Start", command=self.start_search).grid(row=3, column=0, columnspan=4, pady=10)

        # Progress Bar and Status Label
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=4, padx=10, pady=5)

        self.status_label = ttk.Label(self.root, text="", anchor="center", wraplength=400)
        self.status_label.grid(row=5, column=0, columnspan=4, padx=10, pady=5)

    def setup_layout(self):
        self.root.grid_columnconfigure(1, weight=1)  # Make column 1 expandable

    def start_search(self):
        # Reset UI
        self.status_label.config(text="")
        self.progress["value"] = 0

        # Get user inputs
        hash_value = self.hash_var.get().encode()
        max_length = self.max_length_var.get()
        require_digits = self.require_digits_var.get()
        require_letters = self.require_letters_var.get()
        start_with = self.start_with_var.get()

        # Pass search parameters to the decryption function in a separate process
        self.process = multiprocessing.Process(target=decrypt_hash, args=(self.progress_queue, hash_value, max_length, require_digits, require_letters, start_with))
        self.process.start()

        # Monitor progress
        self.monitor_progress()

    def monitor_progress(self):
        if not self.progress_queue.empty():
            current, total, result = self.progress_queue.get()
            self.progress["value"] = (current / total) * 100
            if result:
                self.status_label.config(text=f"Matching combination found: {result}")
                self.process.terminate()
                return

        if self.process.is_alive():
            self.root.after(100, self.monitor_progress)
        else:
            self.process.join()
            self.status_label.config(text="No matching combination found.")

# Main
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    root = tk.Tk()
    app = HashDecryptorApp(root)
    root.mainloop()
