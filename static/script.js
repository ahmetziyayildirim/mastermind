let gameId = null;
let lastGames = [];

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
    try {
        const response = await fetch('/new-game', {
            method: 'POST'
        });
        const data = await response.json();
        gameId = data.game_id;
        lastGames = data.last_games || [];  // Ensure lastGames is initialized
        
        // Reset UI
        document.getElementById('history').innerHTML = '';
        document.getElementById('attempts').textContent = '0';
        document.getElementById('guess-input').value = '';
        document.getElementById('guess-input').focus();
        
        // Update last games display immediately
        updateLastGamesDisplay();
    } catch (error) {
        console.error('Error starting new game:', error);
    }
}

function updateLastGamesDisplay() {
    const lastGamesList = document.getElementById('last-games-list');
    lastGamesList.innerHTML = '';
    
    if (!lastGames || lastGames.length === 0) {
        lastGamesList.innerHTML = '<div class="history-item">No previous games</div>';
        return;
    }
    
    lastGames.forEach(game => {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        const resultEmoji = game.won ? '🎉 Won' : '😔 Lost';
        const resultClass = game.won ? 'win-message' : 'lose-message';
        item.classList.add(resultClass);
        
        // Create game summary
        let html = `
            ${resultEmoji} in ${game.attempts} attempts
            <br>
            <small>Code: ${game.secret_code} | ${game.timestamp}</small>
        `;
        
        // Add guess history if available
        if (game.guesses && game.guesses.length > 0) {
            html += '<div class="guess-history">';
            game.guesses.forEach((guess, index) => {
                html += `<div class="guess-item">
                    #${index + 1}: ${guess.guess} → ${guess.feedback}
                </div>`;
            });
            html += '</div>';
        }
        
        item.innerHTML = html;
        lastGamesList.appendChild(item);
    });
}

async function submitGuess() {
    const guessInput = document.getElementById('guess-input');
    const guess = guessInput.value;
    
    if (guess.length !== 4 || !/^\d+$/.test(guess)) {
        alert('Please enter exactly 4 digits');
        return;
    }
    
    try {
        const response = await fetch('/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                guess: guess  // Remove game_id from request
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
                await startNewGame();
            }
        } else {
            if (data.error === 'No active game. Please start a new game.') {
                await startNewGame();
            } else {
                alert(data.error || 'An error occurred');
            }
        }
    } catch (error) {
        console.error('Error submitting guess:', error);
        alert('An error occurred. Please try again.');
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