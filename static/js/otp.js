// OTP Request Handler
document.addEventListener('DOMContentLoaded', function() {
    // Add OTP request functionality if button exists
    const requestOtpBtn = document.getElementById('requestOtp');
    if (requestOtpBtn) {
        requestOtpBtn.addEventListener('click', function() {
            const username = document.getElementById('login-username').value;
            if (!username) {
                alert('Please enter your username first');
                return;
            }
            
            // Show loading state
            this.textContent = 'Sending...';
            this.disabled = true;
            
            // Enable the OTP field if it was disabled
            const otpInput = document.getElementById('otp');
            if (otpInput) {
                otpInput.disabled = false;
                otpInput.placeholder = "OTP Code";
            }
            
            console.log('Sending OTP for user:', username);
            fetch("/send_otp", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ username })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                document.getElementById('requestOtp').textContent = 'Request OTP';
                document.getElementById('requestOtp').disabled = false;
                
                if (data.status === 'success') {
                    // Show success message
                    const messageElement = document.getElementById('message');
                    if (messageElement) {
                        messageElement.textContent = 'OTP sent to your email. Please check your inbox and enter the code.';
                        messageElement.className = 'success-message';
                    } else {
                        alert('OTP sent to your email. Please check your inbox and enter the code.');
                    }
                    
                    // Focus on OTP input field if it exists
                    const otpInput = document.getElementById('otp');
                    if (otpInput) {
                        otpInput.focus();
                    }
                    
                    // Start the countdown timer - OTP valid for 10 minutes (600 seconds)
                    startOtpCountdown(600);
                } else if (data.status === 'warning') {
                    // Handle development mode with network issues
                    const messageElement = document.getElementById('message');
                    if (messageElement) {
                        messageElement.textContent = data.message;
                        messageElement.className = 'warning-message';
                    } else {
                        alert(data.message);
                    }
                    
                    // Focus on OTP input field if it exists
                    const otpInput = document.getElementById('otp');
                    if (otpInput) {
                        otpInput.focus();
                        // In development mode, pre-fill the OTP for testing
                        if (data.otp) {
                            otpInput.value = data.otp;
                        }
                    }
                    
                    // Start the countdown timer - OTP valid for 10 minutes (600 seconds)
                    startOtpCountdown(600);
                } else {
                    // Show error message
                    const messageElement = document.getElementById('message');
                    if (messageElement) {
                        messageElement.textContent = data.message || 'Failed to send OTP. Please try again.';
                        messageElement.className = 'error-message';
                    } else {
                        alert(data.message || 'Failed to send OTP. Please try again.');
                    }
                }
            })
            .catch(error => {
                // Reset button
                document.getElementById('requestOtp').textContent = 'Request OTP';
                document.getElementById('requestOtp').disabled = false;
                
                console.error('Error:', error);
                alert('An error occurred while requesting the OTP.');
            });
        });
    }
    
    // Hide OTP timer when login form is submitted
    const loginForm = document.querySelector('.sign-in form');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const timerElement = document.getElementById('otp-timer');
            if (timerElement) {
                timerElement.style.display = 'none';
            }
            
            // Clear any existing timer
            if (window.otpCountdownInterval) {
                clearInterval(window.otpCountdownInterval);
            }
        });
    }
});

// OTP Countdown Timer Function
function startOtpCountdown(duration) {
    const timerElement = document.getElementById('otp-timer');
    const countdownElement = document.getElementById('countdown');
    
    // Display the timer
    timerElement.style.display = 'block';
    
    // Initialize timer variables
    let timer = duration;
    let minutes, seconds;
    
    // Clear any existing timer
    if (window.otpCountdownInterval) {
        clearInterval(window.otpCountdownInterval);
    }
    
    // Update the countdown timer immediately and then every second
    updateCountdown();
    window.otpCountdownInterval = setInterval(updateCountdown, 1000);
    
    function updateCountdown() {
        // Calculate minutes and seconds
        minutes = Math.floor(timer / 60);
        seconds = timer % 60;
        
        // Format the time with leading zeros if needed
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;
        
        // Update the countdown display
        countdownElement.textContent = minutes + ":" + seconds;
        
        // Change color to indicate urgency when time is running out
        if (timer <= 60) { // Last minute
            countdownElement.style.color = "#ff3860"; // Red color for urgency
        } else {
            countdownElement.style.color = "#00C3B5"; // Default color
        }
        
        // Decrease the timer
        if (--timer < 0) {
            // Timer has expired
            clearInterval(window.otpCountdownInterval);
            timerElement.innerHTML = '<span style="color: #ff3860;">OTP has expired. Please request a new code.</span>';
            
            // Disable the OTP field
            const otpInput = document.getElementById('otp');
            if (otpInput) {
                otpInput.disabled = true;
                otpInput.placeholder = "Expired";
                otpInput.value = "";
            }
        }
    }
}
