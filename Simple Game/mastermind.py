import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class MastermindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Mastermind")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#2C3E50')  # Dark blue background
        
        # Game variables
        self.secret_code = self.generate_secret_code()
        self.attempts = 0
        self.max_attempts = 10
        
        # GUI elements
        self.create_widgets()
        
        # Bind Enter key to submit_guess
        self.root.bind('<Return>', lambda event: self.process_guess())
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title with fancy styling
        title = tk.Label(main_frame, 
                        text="Number Mastermind",
                        font=("Helvetica", 24, "bold"),
                        fg='#E74C3C',  # Red text
                        bg='#2C3E50')
        title.pack(pady=10)
        
        # Instructions with better styling
        instructions = tk.Label(main_frame,
                              text="Enter a 4-digit number (0-9)",
                              font=("Helvetica", 12),
                              fg='#ECF0F1',  # Light gray text
                              bg='#2C3E50')
        instructions.pack()
        
        # Entry field with better styling
        entry_frame = tk.Frame(main_frame, bg='#2C3E50')
        entry_frame.pack(pady=15)
        
        self.guess_entry = tk.Entry(entry_frame,
                                  font=("Helvetica", 18),
                                  width=8,
                                  justify='center',
                                  bg='#ECF0F1',
                                  fg='#2C3E50')
        self.guess_entry.pack(pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(pady=5)
        
        # Submit button with hover effect
        style = ttk.Style()
        style.configure('Submit.TButton', 
                       font=('Helvetica', 12),
                       padding=10)
        
        submit_btn = ttk.Button(button_frame,
                               text="Submit Guess",
                               style='Submit.TButton',
                               command=self.process_guess)
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # New Game button
        new_game_btn = ttk.Button(button_frame,
                                 text="New Game",
                                 style='Submit.TButton',
                                 command=self.new_game)
        new_game_btn.pack(side=tk.LEFT, padx=5)
        
        # History frame with better styling
        history_frame = tk.Frame(main_frame, bg='#34495E')  # Slightly lighter blue
        history_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History display with better styling
        self.history_display = tk.Text(history_frame,
                                     height=15,
                                     width=35,
                                     font=("Courier", 12),
                                     bg='#34495E',
                                     fg='#ECF0F1',
                                     yscrollcommand=scrollbar.set)
        self.history_display.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        scrollbar.config(command=self.history_display.yview)
        
        # Attempts counter with better styling
        self.attempts_label = tk.Label(main_frame,
                                     text=f"Attempts: 0/{self.max_attempts}",
                                     font=("Helvetica", 12, "bold"),
                                     fg='#E74C3C',
                                     bg='#2C3E50')
        self.attempts_label.pack(pady=10)

    def generate_secret_code(self):
        return [random.randint(0, 9) for _ in range(4)]

    def evaluate_guess(self, guess):
        correct_position = 0
        correct_digit = 0
        
        # Convert guess to list of integers
        guess = [int(d) for d in guess]
        
        # Check for correct positions
        for i in range(4):
            if guess[i] == self.secret_code[i]:
                correct_position += 1
        
        # Check for correct digits in wrong positions
        guess_copy = guess.copy()
        secret_copy = self.secret_code.copy()
        
        # Remove correct positions from both lists
        for i in range(3, -1, -1):
            if guess_copy[i] == secret_copy[i]:
                guess_copy.pop(i)
                secret_copy.pop(i)
        
        # Count remaining correct digits in wrong positions
        for digit in guess_copy:
            if digit in secret_copy:
                correct_digit += 1
                secret_copy.remove(digit)
        
        return correct_position, correct_digit

    def process_guess(self):
        guess = self.guess_entry.get()
        
        # Validate input
        if len(guess) != 4 or not guess.isdigit():
            messagebox.showerror("Error", "Please enter exactly 4 digits!")
            return
        
        self.attempts += 1
        self.attempts_label.config(text=f"Attempts: {self.attempts}/{self.max_attempts}")
        
        correct_pos, correct_digits = self.evaluate_guess(guess)
        
        # Create feedback string with colors using tags
        if correct_pos == 0 and correct_digits == 0:
            feedback = "0"
        else:
            feedback = ""
            if correct_pos > 0:
                feedback += f"+{correct_pos} "
            if correct_digits > 0:
                feedback += f"-{correct_digits}"
        
        # Add to history with colored feedback
        result = f"Guess #{self.attempts}: {guess} → {feedback}\n"
        
        self.history_display.insert(tk.END, result)
        self.history_display.see(tk.END)
        self.guess_entry.delete(0, tk.END)
        
        # Check win/lose conditions
        if correct_pos == 4:
            messagebox.showinfo("Congratulations! 🎉", f"You won in {self.attempts} attempts!")
            self.new_game()
        elif self.attempts >= self.max_attempts:
            secret_code_str = ''.join(map(str, self.secret_code))
            messagebox.showinfo("Game Over 😔", f"You've run out of attempts!\nThe secret code was: {secret_code_str}")
            self.new_game()

    def new_game(self):
        self.secret_code = self.generate_secret_code()
        self.attempts = 0
        self.attempts_label.config(text=f"Attempts: {self.attempts}/{self.max_attempts}")
        self.history_display.delete(1.0, tk.END)
        self.guess_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = MastermindGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 