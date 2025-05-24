"""
Script to create a clean index.html file with OTP functionality
"""
import os

CLEAN_HTML = '''{% extends 'user/base.html' %}

{% block head %}
<title>Log In or Sign Up | RiddleNet</title>
<style>
    body {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        height: 100vh;
        position: relative;
    }
    
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        object-fit: cover;
    }
    
    #overview {
        width: 190px;
        height: 55px;
        background: #00C3B5;
        border: 2px solid #fff;
        outline: none;
        border-radius: 6px;
        font-size: 18px;
        color: #fff;
        letter-spacing: 1px;
        font-weight: 600;
        margin-top: 20px;
        cursor: pointer;
        transition: 0.5s;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-left: auto;
        margin-right: auto;
    }

    #overview:hover {
        background: transparent;
        box-shadow: none;
    }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<link rel="icon" href="{{ url_for('static', filename='img/Logo.png') }}">
{% endblock %}

{% block body %}
<video class="video-background" autoplay muted loop playsinline>
    <source src="{{ url_for('static', filename='video/RiddleNet.mp4') }}" type="video/mp4">
</video>

<div class="container" id="container">
    <div class="form-container sign-up">
        <form action="{{ url_for('user.signup') }}" method="POST" id="signupForm">
            <img id="signup-logo" style="height: 200px; width: 200px;"  
            src="{{ url_for('static', filename='img/Logo.png') }}" alt="Logo">
            <h1>Create Account</h1>
            <input type="text" name="username" placeholder="Username" required autocomplete="off">
            <input type="email" name="email" placeholder="Email" required autocomplete="off">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign Up</button>
            
        </form>
    </div>
    <div class="form-container sign-in">
        <form action="{{ url_for('user.login') }}" method="POST">
            <img style="height: 150px; width: 150px;"         
            src="{{ url_for('static', filename='img/Logo.png') }}" alt="Logo">
            <h1>Sign In</h1>
            {% if next %}
            <input type="hidden" name="next" value="{{ next }}">
            {% endif %}
            <input type="text" name="username" id="login-username" placeholder="Username" required autocomplete="off">
            <input type="password" name="password" placeholder="Password" required>
            <div style="display: flex; width: 100%;">
                <input type="text" name="otp" placeholder="OTP Code" style="flex: 1; margin-right: 10px;">
                <button type="button" id="requestOtp" style="flex: none; width: auto; padding: 10px; background: #00C3B5; font-size: 12px;">Request OTP</button>
            </div>
            <button type="submit">Sign In</button>
        </form>
    </div>
    <div class="toggle-container">
        <div class="toggle">
            <div class="toggle-panel toggle-left">
                <h1>Welcome RiddleNet</h1>
                <p></p>
                <button class="hidden" id="login">Sign In</button>
            </div>
            <div class="toggle-panel toggle-right">
                <h1>RiddleNet</h1>
                <p>Register</p>
                <button class="hidden" id="register">Sign Up</button>
            </div>
        </div>
    </div>
</div>

<!--<button id="overview">Overview</button>-->
{% if message %}
<script>
    alert("{{ message }}");
</script>
{% endif %}
<script src="{{ url_for('static', filename='js/otp.js') }}"></script>
<script>
    function playClickSound() {
        const audio = document.getElementById('clickSound');
        audio.currentTime = 0;
        audio.play();
    }

    // Add click sound to all buttons
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', playClickSound);
    });

    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');
    const overviewBtn = document.getElementById('overview');

    registerBtn.addEventListener('click', () => {
        playClickSound();
        container.classList.add("active");
    });

    loginBtn.addEventListener('click', () => {
        playClickSound();
        container.classList.remove("active");
    });

    overviewBtn && overviewBtn.addEventListener('click', () => {
        playClickSound();
        window.location.href="{{ url_for('user.overview') }}";
    });

    document.querySelector('.sign-up form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting the traditional way
        const formData = new FormData(this);
        const username = formData.get('username');

        fetch("{{ url_for('user.signup') }}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                // Show alert for existing username
                alert(data.message);
                // Clear only the username field and focus on it
                document.querySelector('input[name="username"]').value = '';
                document.querySelector('input[name="username"]').focus();
                return Promise.reject('Username exists'); // Stop the chain
            }
            
            // Show success message and switch to login form
            alert(data.message);
            container.classList.remove("active");
        })
        .catch(error => {
            if (error === 'Username exists') return; // Already handled
            console.error('Error:', error);
            alert('An error occurred while creating the account');
        });
    });
</script>
<audio id="clickSound" src="{{ url_for('static', filename='audio/Start.mp3') }}"></audio>
{% endblock %}'''

# Write the clean HTML file
file_path = 'templates/user/index.html'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(CLEAN_HTML)

print(f"Created clean index.html with OTP functionality")
