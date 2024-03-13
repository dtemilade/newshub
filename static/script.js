document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelectorAll('.nav-links li a');
    let inactivityTimeout;
    let timeoutCounter;

    function sendVerificationCode(email, phone) {
        const accountSid = 'ACb1aba7e3875a09f4b3a41a56b258db76';
        const authToken = 'f8bcbdfa638b8b465618bbb429fa70f4';
        const client = require('twilio')(accountSid, authToken);

        // Generate a random 6-digit verification code
        const verificationCode = Math.floor(100000 + Math.random() * 900000);

        client.messages
            .create({
                body: 'Your verification code is: ' + verificationCode,
                from: '09164441596',
                to: phone, email
            })
            .then(message => console.log(message.sid))
            .catch(error => console.error(error));
    }

    document.getElementById('registerForm').addEventListener('submit', function(event) {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone_number').value;

        // Send AJAX request to send_verification_code route
        fetch('/send_verification_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, phone_number: phone })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Verification code sent successfully!');
            } else {
                alert('Failed to send verification code.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while sending the verification code.');
        });
    });

    function resetTimeout() {
        clearTimeout(inactivityTimeout);
        clearTimeout(timeoutCounter);

        inactivityTimeout = setTimeout(logoutUser, 5 * 60 * 1000); // 5 minutes in milliseconds
        startTimeoutCounter();
    }

    function startTimeoutCounter() {
        let seconds = 300; // 5 minutes in seconds
        timeoutCounter = setInterval(() => {
            document.getElementById('timeout-counter').textContent = seconds;
            seconds--;

            if (seconds === 60) {
                document.getElementById('timeout-notification').style.display = 'block';
            }

            if (seconds < 0) {
                logoutUser();
            }
        }, 1000);
    }

    function logoutUser() {
        document.body.classList.remove('nav-open');
        window.location.href = '/logout';
    }

    navToggle.addEventListener('click', () => {
        document.body.classList.toggle('nav-open');
        resetTimeout();
    });

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            document.body.classList.remove('nav-open');
            resetTimeout();
        });
    });

    resetTimeout();
});
