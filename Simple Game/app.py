from flask import Flask, render_template, jsonify, request
import random
from datetime import datetime, timedelta
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Store game states (in a real production app, you'd want to use a proper database)
games = {}

def generate_secret_code():
    return [random.randint(0, 9) for _ in range(4)]

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new-game', methods=['POST'])
def new_game():
    # Clean up old games
    cleanup_old_games()
    
    game_id = random.randint(10000, 99999)
    games[game_id] = {
        'secret_code': generate_secret_code(),
        'attempts': 0,
        'max_attempts': 10,
        'history': [],
        'timestamp': datetime.now()  # Add timestamp
    }
    return jsonify({'game_id': game_id})

def cleanup_old_games():
    """Remove games older than 1 hour to prevent memory leaks"""
    current_time = datetime.now()
    expired_games = [
        game_id for game_id, game in games.items()
        if current_time - game['timestamp'] > timedelta(hours=1)
    ]
    for game_id in expired_games:
        del games[game_id]

@app.route('/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    game_id = data['game_id']
    guess = data['guess']
    
    if game_id not in games:
        return jsonify({'error': 'Invalid game'}), 400
    
    game = games[game_id]
    
    if game['attempts'] >= game['max_attempts']:
        return jsonify({'error': 'Game over'}), 400
    
    if len(guess) != 4 or not guess.isdigit():
        return jsonify({'error': 'Invalid guess'}), 400
    
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
    
    result = {
        'guess': guess,
        'feedback': feedback.strip(),
        'attempt': game['attempts'],
        'game_over': correct_pos == 4 or game['attempts'] >= game['max_attempts'],
        'won': correct_pos == 4,
        'secret_code': ''.join(map(str, game['secret_code'])) if correct_pos == 4 or game['attempts'] >= game['max_attempts'] else None
    }
    
    game['history'].append(result)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run() 