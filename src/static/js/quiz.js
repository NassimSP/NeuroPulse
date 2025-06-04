/**
 * Neurodivergent-Friendly Quiz Application
 * JavaScript functionality for quiz interactions
 */

class QuizApp {
    constructor() {
        this.currentQuestion = 0;
        this.selectedAnswer = null;
        this.confidenceLevel = 3;
        this.quizData = null;
        this.answers = [];
        
        this.init();
    }
    
    init() {
        // Initialize event listeners and load quiz data
        this.bindEvents();
        this.loadProgress();
        
        // Start the quiz if we're on the quiz page
        if (document.querySelector('.quiz-container')) {
            this.startQuiz();
        }
    }
    
    bindEvents() {
        // Confidence slider
        const confidenceSlider = document.getElementById('confidence-slider');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                this.confidenceLevel = parseInt(e.target.value);
                this.updateConfidenceDisplay();
            });
        }
        
        // Submit answer button
        const submitBtn = document.getElementById('submit-answer');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitAnswer());
        }
        
        // Next question button
        const nextBtn = document.getElementById('next-question');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }
        
        // Restart quiz button
        const restartBtn = document.getElementById('restart-quiz');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartQuiz());
        }
        
        // Progress tracking in localStorage
        this.loadProgress();
    }
    
    startQuiz() {
        const quizContainer = document.querySelector('.quiz-container');
        if (!quizContainer) return;
        
        const quizId = quizContainer.dataset.quizId;
        if (quizId) {
            this.loadQuestion(quizId, 0);
        }
    }
    
    async loadQuestion(quizId, questionNum) {
        try {
            this.showLoading();
            
            const response = await fetch(`/api/quiz/${quizId}/question/${questionNum}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.quizData = data;
            this.currentQuestion = questionNum;
            this.selectedAnswer = null;
            
            this.renderQuestion(data);
            this.updateProgress();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading question:', error);
            this.showError('Failed to load question. Please try again.');
            this.hideLoading();
        }
    }
    
    renderQuestion(data) {
        const container = document.querySelector('.quiz-container');
        if (!container) return;
        
        // Update question counter
        const counter = document.querySelector('.question-counter');
        if (counter) {
            counter.textContent = `Question ${data.question_number} of ${data.total_questions}`;
        }
        
        // Update progress bar
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const progress = (data.question_number / data.total_questions) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Update question text
        const questionText = document.querySelector('.question-text');
        if (questionText) {
            questionText.textContent = data.question.question;
        }
        
        // Render answer options
        this.renderAnswerOptions(data.question.options);
        
        // Reset UI state
        this.hideSubmitButton();
        this.hideFeedback();
        this.hideNextButton();
        this.resetConfidence();
    }
    
    renderAnswerOptions(options) {
        const container = document.querySelector('.answers-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        options.forEach((option, index) => {
            const button = document.createElement('button');
            button.className = 'answer-option';
            button.textContent = option;
            button.setAttribute('data-answer', option);
            
            button.addEventListener('click', () => this.selectAnswer(option, button));
            
            container.appendChild(button);
        });
    }
    
    selectAnswer(answer, buttonElement) {
        // Remove previous selection
        document.querySelectorAll('.answer-option').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select new answer
        buttonElement.classList.add('selected');
        this.selectedAnswer = answer;
        
        // Show submit button with animation
        this.showSubmitButton();
        
        // Add haptic feedback for mobile devices
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
    }
    
    async submitAnswer() {
        if (!this.selectedAnswer) {
            this.showError('Please select an answer before submitting.');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await fetch('/api/quiz/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    answer: this.selectedAnswer,
                    confidence: this.confidenceLevel
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                this.showError(result.error);
                return;
            }
            
            // Show feedback
            this.showFeedback(result);
            
            // Update answer options to show correct/incorrect
            this.updateAnswerDisplay(result);
            
            // Hide submit button, show next button or results
            this.hideSubmitButton();
            
            if (result.is_complete) {
                this.showResultsButton(result.results_url);
                this.triggerCelebration();
            } else {
                this.showNextButton();
            }
            
            // Save progress
            this.saveProgress();
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Error submitting answer:', error);
            this.showError('Failed to submit answer. Please try again.');
            this.hideLoading();
        }
    }
    
    showFeedback(result) {
        const feedback = document.querySelector('.feedback');
        if (!feedback) return;
        
        feedback.className = `feedback ${result.is_correct ? 'correct' : 'incorrect'} show`;
        
        const icon = result.is_correct ? '🎉' : '🤔';
        const message = result.is_correct ? 'Excellent!' : 'Not quite right.';
        
        // Clear existing content
        feedback.innerHTML = '';
        
        // Create icon and message elements safely
        const iconSpan = document.createElement('span');
        iconSpan.className = 'feedback-icon';
        iconSpan.textContent = icon;
        feedback.appendChild(iconSpan);
        
        const messageText = document.createTextNode(message);
        feedback.appendChild(messageText);
        
        // Add explanation safely if present
        if (result.explanation) {
            const explanationDiv = document.createElement('div');
            explanationDiv.style.marginTop = '1rem';
            explanationDiv.style.fontWeight = 'normal';
            explanationDiv.textContent = result.explanation; // Safe text content, no HTML
            feedback.appendChild(explanationDiv);
        }
        
        // Add celebration sound for correct answers (if audio is enabled)
        if (result.is_correct) {
            this.playSuccessSound();
        }
    }
    
    updateAnswerDisplay(result) {
        document.querySelectorAll('.answer-option').forEach(btn => {
            const answerText = btn.getAttribute('data-answer');
            
            if (answerText === result.correct_answer) {
                btn.classList.add('correct');
            } else if (answerText === this.selectedAnswer && !result.is_correct) {
                btn.classList.add('incorrect');
            }
            
            // Disable all buttons
            btn.disabled = true;
            btn.style.cursor = 'default';
        });
    }
    
    nextQuestion() {
        const nextQuestionNum = this.currentQuestion + 1;
        const quizId = document.querySelector('.quiz-container').dataset.quizId;
        this.loadQuestion(quizId, nextQuestionNum);
    }
    
    restartQuiz() {
        if (confirm('Are you sure you want to restart the quiz? All progress will be lost.')) {
            fetch('/api/quiz/reset')
                .then(() => {
                    window.location.reload();
                })
                .catch(error => {
                    console.error('Error restarting quiz:', error);
                    window.location.reload();
                });
        }
    }
    
    triggerCelebration() {
        // Create confetti animation
        this.createConfetti();
        
        // Add celebration class to body for CSS animations
        document.body.classList.add('celebrating');
        
        // Remove celebration class after animation
        setTimeout(() => {
            document.body.classList.remove('celebrating');
        }, 3000);
    }
    
    createConfetti() {
        const colors = ['#1E7ED8', '#27AE60', '#FF8C00', '#E74C3C', '#FFD700'];
        const celebrationContainer = document.createElement('div');
        celebrationContainer.className = 'celebration';
        document.body.appendChild(celebrationContainer);
        
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
            celebrationContainer.appendChild(confetti);
        }
        
        // Clean up confetti after animation
        setTimeout(() => {
            celebrationContainer.remove();
        }, 6000);
    }
    
    playSuccessSound() {
        // Create a simple success sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
            oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            // Audio not supported or blocked, fail silently
            console.log('Audio not available');
        }
    }
    
    updateProgress() {
        const progressData = {
            currentQuestion: this.currentQuestion,
            answers: this.answers,
            timestamp: Date.now()
        };
        
        localStorage.setItem('quiz_progress', JSON.stringify(progressData));
    }
    
    loadProgress() {
        try {
            const saved = localStorage.getItem('quiz_progress');
            if (saved) {
                const data = JSON.parse(saved);
                this.currentQuestion = data.currentQuestion || 0;
                this.answers = data.answers || [];
            }
        } catch (error) {
            console.log('No saved progress found');
        }
    }
    
    saveProgress() {
        this.updateProgress();
    }
    
    updateConfidenceDisplay() {
        const labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High'];
        const display = document.querySelector('.confidence-display');
        if (display) {
            display.textContent = labels[this.confidenceLevel - 1];
        }
    }
    
    resetConfidence() {
        this.confidenceLevel = 3;
        const slider = document.getElementById('confidence-slider');
        if (slider) {
            slider.value = 3;
        }
        this.updateConfidenceDisplay();
    }
    
    // UI helper methods
    showLoading() {
        const btn = document.getElementById('submit-answer') || document.getElementById('next-question');
        if (btn) {
            btn.innerHTML = '<div class="loading"></div>';
            btn.disabled = true;
        }
    }
    
    hideLoading() {
        const submitBtn = document.getElementById('submit-answer');
        const nextBtn = document.getElementById('next-question');
        
        if (submitBtn) {
            submitBtn.innerHTML = 'Submit Answer';
            submitBtn.disabled = false;
        }
        
        if (nextBtn) {
            nextBtn.innerHTML = 'Next Question';
            nextBtn.disabled = false;
        }
    }
    
    showSubmitButton() {
        const btn = document.getElementById('submit-answer');
        if (btn) {
            btn.style.display = 'block';
            btn.classList.add('btn-primary');
        }
    }
    
    hideSubmitButton() {
        const btn = document.getElementById('submit-answer');
        if (btn) {
            btn.style.display = 'none';
        }
    }
    
    showNextButton() {
        const btn = document.getElementById('next-question');
        if (btn) {
            btn.style.display = 'block';
            btn.classList.add('btn-primary');
        }
    }
    
    hideNextButton() {
        const btn = document.getElementById('next-question');
        if (btn) {
            btn.style.display = 'none';
        }
    }
    
    showResultsButton(url) {
        const container = document.querySelector('.quiz-actions');
        if (container) {
            const btn = document.createElement('a');
            btn.href = url;
            btn.className = 'btn btn-success btn-lg btn-block';
            btn.innerHTML = '🎉 View Results';
            btn.style.display = 'block';
            container.appendChild(btn);
        }
    }
    
    hideFeedback() {
        const feedback = document.querySelector('.feedback');
        if (feedback) {
            feedback.classList.remove('show');
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '20px';
        errorDiv.style.right = '20px';
        errorDiv.style.zIndex = '9999';
        errorDiv.style.maxWidth = '400px';
        
        // Create elements safely to prevent XSS
        const strongEl = document.createElement('strong');
        strongEl.textContent = 'Error: ';
        errorDiv.appendChild(strongEl);
        
        const messageText = document.createTextNode(message);
        errorDiv.appendChild(messageText);
        
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.style.cssText = 'float: right; background: none; border: none; font-size: 1.2em; cursor: pointer;';
        closeBtn.textContent = '×';
        closeBtn.onclick = function() { this.parentElement.remove(); };
        errorDiv.appendChild(closeBtn);
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the quiz app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.quizApp = new QuizApp();
});

// Export for potential testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuizApp;
}
