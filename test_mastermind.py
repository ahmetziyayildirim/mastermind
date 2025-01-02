import requests
import time
import random

def generate_valid_guess():
    """Generate a valid guess following the rules:
    1. No repeating digits
    2. Cannot start with 0
    """
    # First digit: 1-9
    first_digit = random.randint(1, 9)
    
    # Remaining digits: 0-9 excluding used digits
    remaining_digits = list(range(10))
    remaining_digits.remove(first_digit)
    
    # Randomly select 3 more unique digits
    other_digits = random.sample(remaining_digits, 3)
    
    # Combine and convert to string
    return ''.join(map(str, [first_digit] + other_digits))

class MastermindTester:
    def __init__(self, base_url='http://localhost:10000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.game_id = None
        
    def start_new_game(self):
        """Start a new game and store the game ID"""
        try:
            response = self.session.post(f'{self.base_url}/new-game')
            data = response.json()
            self.game_id = data['game_id']
            return data
        except Exception as e:
            print(f"Error starting new game: {e}")
            return None
    
    def make_guess(self, guess):
        """Make a guess in the current game"""
        try:
            response = self.session.post(
                f'{self.base_url}/guess',
                json={'guess': guess}
            )
            return response.json()
        except Exception as e:
            print(f"Error making guess: {e}")
            return {'error': str(e)}
    
    def play_random_strategy(self):
        """Play a game using random guesses"""
        print("\nPlaying with random strategy...")
        game_data = self.start_new_game()
        if not game_data:
            print("Failed to start new game")
            return
        
        print(f"Started new game with ID: {self.game_id}")
        
        for attempt in range(10):
            # Generate valid random guess
            guess = generate_valid_guess()
            print(f"\nAttempt {attempt + 1}: Guessing {guess}")
            
            response = self.make_guess(guess)
            if 'error' in response:
                print(f"Error: {response['error']}")
                continue
                
            feedback = response.get('feedback', 'No feedback')
            print(f"Feedback: {feedback}")
            
            if response.get('game_over'):
                if response.get('won'):
                    print(f"Won in {attempt + 1} attempts!")
                else:
                    print(f"Lost. Secret code was: {response.get('secret_code')}")
                break
            
            time.sleep(1)
    
    def play_sequential_strategy(self):
        """Play a game using sequential valid numbers"""
        print("\nPlaying with sequential strategy...")
        game_data = self.start_new_game()
        if not game_data:
            print("Failed to start new game")
            return
        
        print(f"Started new game with ID: {self.game_id}")
        
        # Valid sequential numbers that follow rules
        valid_sequences = [
            '1234', '1235', '1236', '1237', '1238', '1239', '1245', '1246',
            '1247', '1248', '1249', '1256', '1257', '1258', '1259', '1267'
        ]
        
        for attempt in range(10):
            guess = valid_sequences[attempt % len(valid_sequences)]
            print(f"\nAttempt {attempt + 1}: Guessing {guess}")
            
            response = self.make_guess(guess)
            if 'error' in response:
                print(f"Error: {response['error']}")
                continue
                
            feedback = response.get('feedback', 'No feedback')
            print(f"Feedback: {feedback}")
            
            if response.get('game_over'):
                if response.get('won'):
                    print(f"Won in {attempt + 1} attempts!")
                else:
                    print(f"Lost. Secret code was: {response.get('secret_code')}")
                break
            
            time.sleep(1)
    
    def play_repeated_strategy(self):
        """
        This strategy is no longer valid with new rules.
        Replacing with ascending digits strategy.
        """
        print("\nPlaying with ascending digits strategy...")
        game_data = self.start_new_game()
        if not game_data:
            print("Failed to start new game")
            return
        
        print(f"Started new game with ID: {self.game_id}")
        
        # Valid ascending combinations
        ascending_numbers = [
            '1234', '1235', '1236', '1237', '1238', '1239',
            '2345', '2346', '2347', '2348', '2349',
            '3456', '3457', '3458', '3459',
            '4567', '4568', '4569'
        ]
        
        for attempt in range(10):
            guess = ascending_numbers[attempt % len(ascending_numbers)]
            print(f"\nAttempt {attempt + 1}: Guessing {guess}")
            
            response = self.make_guess(guess)
            if 'error' in response:
                print(f"Error: {response['error']}")
                continue
                
            feedback = response.get('feedback', 'No feedback')
            print(f"Feedback: {feedback}")
            
            if response.get('game_over'):
                if response.get('won'):
                    print(f"Won in {attempt + 1} attempts!")
                else:
                    print(f"Lost. Secret code was: {response.get('secret_code')}")
                break
            
            time.sleep(1)

def main():
    tester = MastermindTester()
    
    print("=== Testing Mastermind Game ===")
    
    # Run each strategy
    tester.play_random_strategy()
    time.sleep(2)  # Add delay between strategies
    
    tester.play_sequential_strategy()
    time.sleep(2)
    
    tester.play_repeated_strategy()

if __name__ == "__main__":
    main() 