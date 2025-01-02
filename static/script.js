let gameId = null;
let lastGames = [];
let playerNickname = '';

document.addEventListener('DOMContentLoaded', () => {
    // Show nickname modal first
    showNicknameModal();
    
    startNewGame();
    
    document.getElementById('guess-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    document.getElementById('submit-guess').addEventListener('click', submitGuess);
    document.getElementById('new-game').addEventListener('click', startNewGame);

    // Add number checker functionality
    document.querySelectorAll('.number-item').forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('used')) {
                item.classList.remove('used');
                item.classList.add('possible');
            } else if (item.classList.contains('possible')) {
                item.classList.remove('possible');
            } else {
                item.classList.add('used');
            }
        });
    });

    // Reset checker button
    document.getElementById('reset-checker').addEventListener('click', () => {
        document.querySelectorAll('.number-item').forEach(item => {
            item.classList.remove('used', 'possible');
        });
    });

    // Add nickname modal handler
    document.getElementById('start-playing').addEventListener('click', setNickname);
    document.getElementById('nickname-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            setNickname();
        }
    });
});

async function startNewGame() {
    try {
        const response = await fetch('/new-game', {
            method: 'POST'
        });
        const data = await response.json();
        gameId = data.game_id;
        lastGames = data.last_games || [];
        
        // Reset UI
        document.getElementById('history').innerHTML = '';
        document.getElementById('attempts').textContent = '0';
        document.getElementById('guess-input').value = '';
        document.getElementById('guess-input').focus();
        
        // Update displays
        updateLastGamesDisplay();
        if (data.hall_of_fame) {
            updateHallOfFame(data.hall_of_fame);
        }

        // Reset number checker
        document.querySelectorAll('.number-item').forEach(item => {
            item.classList.remove('used', 'possible');
        });
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
            
            if (data.hall_of_fame) {
                updateHallOfFame(data.hall_of_fame);
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

function updateHallOfFame(hallOfFame) {
    const hallOfFameList = document.getElementById('hall-of-fame-list');
    hallOfFameList.innerHTML = '';
    
    if (!hallOfFame || hallOfFame.length === 0) {
        hallOfFameList.innerHTML = '<div class="fame-item">No records yet</div>';
        return;
    }
    
    hallOfFame.forEach((record, index) => {
        const item = document.createElement('div');
        item.className = 'fame-item';
        
        const position = index + 1;
        const medal = position <= 3 ? ['🥇', '🥈', '🥉'][index] : `${position}.`;
        
        item.innerHTML = `
            <span class="fame-position">${medal}</span>
            <div>
                <strong>${record.player}</strong>
                <br>
                Won in ${record.attempts} attempts
                <span class="fame-details">
                    Code: ${record.secret_code} | ${record.timestamp}
                </span>
            </div>
        `;
        
        hallOfFameList.appendChild(item);
    });
}

function showNicknameModal() {
    const modal = document.getElementById('nickname-modal');
    modal.classList.add('active');
    document.getElementById('nickname-input').focus();
}

async function setNickname() {
    const nicknameInput = document.getElementById('nickname-input');
    const nickname = nicknameInput.value.trim();
    const errorElement = document.getElementById('nickname-error');
    
    if (!nickname) {
        errorElement.textContent = 'Please enter a nickname';
        return;
    }
    
    try {
        const response = await fetch('/set-nickname', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nickname })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            playerNickname = nickname;
            document.getElementById('nickname-modal').classList.remove('active');
            updateWelcomeMessage(nickname);
            startNewGame();
        } else {
            errorElement.textContent = data.error || 'An error occurred';
        }
    } catch (error) {
        errorElement.textContent = 'An error occurred. Please try again.';
    }
}

// Add this function to update welcome message
function updateWelcomeMessage(nickname) {
    const welcomeMessage = document.getElementById('welcome-message');
    welcomeMessage.innerHTML = `Welcome <strong>${nickname}</strong>!`;
} 