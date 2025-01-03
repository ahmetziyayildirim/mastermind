from flask import Flask, render_template, jsonify, request, session
import random
from datetime import datetime, timedelta
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import json
from operator import itemgetter

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Store game states
games = {}
game_history = []  # Initialize as empty list
hall_of_fame = []  # Initialize hall of fame list

# Load history on startup
try:
    if os.path.exists('game_history.json'):
        with open('game_history.json', 'r') as f:
            game_history = json.load(f)
            if not isinstance(game_history, list):
                game_history = []
except:
    game_history = []

# Load hall of fame on startup (add after game_history loading)
try:
    if os.path.exists('hall_of_fame.json'):
        with open('hall_of_fame.json', 'r') as f:
            hall_of_fame = json.load(f)
except:
    hall_of_fame = []

def save_history():
    try:
        with open('game_history.json', 'w') as f:
            json.dump(game_history, f)
    except Exception as e:
        print(f"Error saving history: {e}")

def generate_secret_code():
    """Generate a 4-digit code where:
    1. No digit repeats
    2. First digit cannot be 0
    """
    # First digit: 1-9
    first_digit = random.randint(1, 9)
    
    # Remaining digits: 0-9 excluding used digits
    remaining_digits = list(range(10))
    remaining_digits.remove(first_digit)
    
    # Randomly select 3 more unique digits
    other_digits = random.sample(remaining_digits, 3)
    
    # Combine first digit with other digits
    secret_code = [first_digit] + other_digits
    return secret_code

def validate_guess(guess):
    """Validate that the guess follows the rules:
    1. Must be 4 digits
    2. No repeating digits
    3. Cannot start with 0
    Returns: (bool, str) - (is_valid, error_message)
    """
    if len(guess) != 4 or not guess.isdigit():
        return False, "Please enter exactly 4 digits"
    
    if guess[0] == '0':
        return False, "Number cannot start with 0"
    
    if len(set(guess)) != 4:
        return False, "Digits cannot repeat"
    
    return True, ""

def evaluate_guess(secret_code, guess):
    correct_position = 0
    correct_digit = 0
    
    # Convert guess to list of integers
    guess = [int(d) for d in guess]
    
    # Check for correct positions
    for i in range(4):
        if guess[i] == secret_code[i]:
            correct_position += 1
    
    # Check for correct digits in wrong positions
    guess_copy = guess.copy()
    secret_copy = secret_code.copy()
    
    for i in range(3, -1, -1):
        if guess_copy[i] == secret_copy[i]:
            guess_copy.pop(i)
            secret_copy.pop(i)
    
    for digit in guess_copy:
        if digit in secret_copy:
            correct_digit += 1
            secret_copy.remove(digit)
    
    return correct_position, correct_digit

# Add this function to manage history size
def cleanup_history():
    """Keep only the last 5 games in history"""
    global game_history
    if len(game_history) > 5:
        game_history = game_history[:5]
        save_history()

# Add this function to manage hall of fame
def update_hall_of_fame(game_summary):
    """Update hall of fame with best games"""
    global hall_of_fame
    if game_summary['won']:
        fame_entry = {
            'attempts': game_summary['attempts'],
            'secret_code': game_summary['secret_code'],
            'timestamp': game_summary['timestamp'],
            'player': session.get('nickname', 'Anonymous')  # Use nickname from session
        }
        hall_of_fame.append(fame_entry)
        # Sort by attempts (ascending) and timestamp (descending)
        hall_of_fame.sort(key=lambda x: (x['attempts'], -datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M').timestamp()))
        # Keep only top 10
        hall_of_fame = hall_of_fame[:10]
        save_hall_of_fame()

def save_hall_of_fame():
    """Save hall of fame to a file"""
    try:
        with open('hall_of_fame.json', 'w') as f:
            json.dump(hall_of_fame, f)
    except Exception as e:
        print(f"Error saving hall of fame: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new-game', methods=['POST'])
def new_game():
    # Clean up old games (older than 1 hour)
    current_time = datetime.now()
    old_games = [
        gid for gid, game in games.items()
        if (current_time - datetime.strptime(game['timestamp'], '%Y-%m-%d %H:%M')).total_seconds() > 3600
    ]
    for gid in old_games:
        del games[gid]
    
    game_id = str(random.randint(10000, 99999))
    game = {
        'secret_code': generate_secret_code(),
        'attempts': 0,
        'max_attempts': 10,
        'history': [],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'start_time': datetime.now().timestamp()
    }
    
    games[game_id] = game
    session['current_game'] = game_id
    
    return jsonify({
        'game_id': game_id,
        'last_games': game_history[:5],  # Always return only last 5 games
        'hall_of_fame': hall_of_fame  # Add this line
    })

@app.route('/guess', methods=['POST'])
def make_guess():
    global game_history
    
    data = request.get_json()
    game_id = session.get('current_game')
    guess = data['guess']
    
    if not game_id or game_id not in games:
        return jsonify({'error': 'No active game. Please start a new game.'}), 400
    
    game = games[game_id]
    
    if game['attempts'] >= game['max_attempts']:
        return jsonify({'error': 'Game over'}), 400
    
    # Validate guess
    is_valid, error_message = validate_guess(guess)
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    game['attempts'] += 1
    correct_pos, correct_digits = evaluate_guess(game['secret_code'], guess)
    
    # Create feedback
    if correct_pos == 0 and correct_digits == 0:
        feedback = "0"
    else:
        feedback = ""
        if correct_pos > 0:
            feedback += f"+{correct_pos} "
        if correct_digits > 0:
            feedback += f"-{correct_digits}"
    
    guess_result = {
        'guess': guess,
        'feedback': feedback.strip()
    }
    
    # Store the guess in game history
    if 'guesses' not in game:
        game['guesses'] = []
    game['guesses'].append(guess_result)
    
    result = {
        'guess': guess,
        'feedback': feedback.strip(),
        'attempt': game['attempts'],
        'game_over': correct_pos == 4 or game['attempts'] >= game['max_attempts'],
        'won': correct_pos == 4,
        'secret_code': ''.join(map(str, game['secret_code'])) if correct_pos == 4 or game['attempts'] >= game['max_attempts'] else None
    }
    
    game['history'].append(result)
    
    if result['game_over']:
        end_time = datetime.now().timestamp()
        elapsed_time = int(end_time - game['start_time'])  # Time in seconds
        
        game_summary = {
            'attempts': game['attempts'],
            'won': result['won'],
            'secret_code': ''.join(map(str, game['secret_code'])),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'guesses': game['guesses'],
            'elapsed_time': elapsed_time
        }
        
        # Add new game to history and keep only last 5
        game_history.insert(0, game_summary)
        cleanup_history()  # This will keep only last 5 games
        
        # Clean up completed game from games dictionary
        del games[game_id]
        
        result['last_games'] = game_history
        
        if result['game_over'] and result['won']:
            update_hall_of_fame(game_summary)
            result['hall_of_fame'] = hall_of_fame
    
    return jsonify(result)

@app.route('/set-nickname', methods=['POST'])
def set_nickname():
    data = request.get_json()
    nickname = data.get('nickname', '').strip()
    
    if not nickname:
        return jsonify({'error': 'Nickname cannot be empty'}), 400
    if len(nickname) > 20:
        return jsonify({'error': 'Nickname too long (max 20 characters)'}), 400
    
    session['nickname'] = nickname
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
