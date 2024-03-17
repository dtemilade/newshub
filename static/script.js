document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelectorAll('.nav-links li a');
    let inactivityTimeout;
    let timeoutCounter;

document.addEventListener('DOMContentLoaded', function() {
    const inactivityTimeoutDuration = 5 * 60 * 1000; // 5 minutes in milliseconds
    let inactivityTimeout;

    function resetTimeout() {
        clearTimeout(inactivityTimeout);
        inactivityTimeout = setTimeout(logoutUser, inactivityTimeoutDuration);
    }

    function logoutUser() {
        window.location.href = '/logout';
    }

    // Reset the timeout whenever there is user activity
    document.addEventListener('mousemove', resetTimeout);
    document.addEventListener('keydown', resetTimeout);

    // Initial call to resetTimeout
    resetTimeout();
});


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
