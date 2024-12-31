# Number Mastermind Game

A colorful implementation of the Mastermind game using numbers.

## How to Play
- Guess the secret 4-digit number
- After each guess, you'll get feedback:
  - `+n`: n digits are correct and in the right position
  - `-n`: n digits are correct but in the wrong position
  - `0`: no correct digits

## Installation

### Option 1: Run from Source
1. Make sure you have Python 3.x installed
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python mastermind.py
   ```

### Option 2: Windows Executable
1. Download `mastermind.exe` from the releases section
2. Double-click to run

## Controls
- Enter a 4-digit number
- Press Enter or click "Submit Guess" to make a guess
- Click "New Game" to start over

## Features
- Modern, colorful UI
- Up to 10 attempts per game
- History of all guesses with feedback
- Keyboard support (Enter to submit) 