let gameId = null;

document.addEventListener('DOMContentLoaded', () => {
    startNewGame();
    
    document.getElementById('guess-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    document.getElementById('submit-guess').addEventListener('click', submitGuess);
    document.getElementById('new-game').addEventListener('click', startNewGame);
});

async function startNewGame() {
    const response = await fetch('/new-game', {
        method: 'POST'
    });
    const data = await response.json();
    gameId = data.game_id;
    
    // Reset UI
    document.getElementById('history').innerHTML = '';
    document.getElementById('attempts').textContent = '0';
    document.getElementById('guess-input').value = '';
    document.getElementById('guess-input').focus();
}

async function submitGuess() {
    const guessInput = document.getElementById('guess-input');
    const guess = guessInput.value;
    
    if (guess.length !== 4 || !/^\d+$/.test(guess)) {
        alert('Please enter exactly 4 digits');
        return;
    }
    
    const response = await fetch('/guess', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_id: gameId,
            guess: guess
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        updateHistory(data);
        document.getElementById('attempts').textContent = data.attempt;
        guessInput.value = '';
        
        if (data.game_over) {
            if (data.won) {
                alert(`Congratulations! You won in ${data.attempt} attempts!`);
            } else {
                alert(`Game Over! The secret code was ${data.secret_code}`);
            }
            startNewGame();
        }
    } else {
        alert(data.error);
    }
}

function updateHistory(result) {
    const history = document.getElementById('history');
    const item = document.createElement('div');
    item.className = 'history-item';
    
    if (result.won) {
        item.classList.add('win-message');
    }
    
    item.textContent = `Guess #${result.attempt}: ${result.guess} → ${result.feedback}`;
    history.insertBefore(item, history.firstChild);
} 