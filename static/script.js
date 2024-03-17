document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle'); // Find the element with the class 'nav-toggle'
    const navLinks = document.querySelectorAll('.nav-links li a'); // Find all anchor tags inside list items with the class 'nav-links'
    let inactivityTimeout; // Declare a variable to hold the inactivity timeout
    let timeoutCounter; // Declare a variable to hold the timeout counter

    // Function to reset the inactivity timeout
    function resetTimeout() {
        clearTimeout(inactivityTimeout); // Clear any existing timeout
        inactivityTimeout = setTimeout(logoutUser, inactivityTimeoutDuration); // Set a new timeout to logout user after a period of inactivity
    }

    // Function to logout user by redirecting to '/logout'
    function logoutUser() {
        window.location.href = '/logout'; // Redirect the user to the logout page
    }

    // Event listeners to detect user activity and reset the timeout
    document.addEventListener('mousemove', resetTimeout); // Listen for mouse movement
    document.addEventListener('keydown', resetTimeout); // Listen for keyboard activity

    // Call resetTimeout function when the page loads
    resetTimeout();
});

// Function to start a counter for logout
function startTimeoutCounter() {
    let seconds = 300; // Set the timeout duration to 5 minutes in seconds
    timeoutCounter = setInterval(() => {
        document.getElementById('timeout-counter').textContent = seconds; // Display the remaining seconds on the page
        seconds--; // Decrement the remaining seconds

        // Display a notification when 60 seconds are remaining
        if (seconds === 60) {
            document.getElementById('timeout-notification').style.display = 'block';
        }

        // Logout the user when the timeout expires
        if (seconds < 0) {
            logoutUser();
        }
    }, 1000); // Update the counter every second
}

// Function to logout user by removing navigation menu and redirecting to '/logout'
function logoutUser() {
    document.body.classList.remove('nav-open'); // Remove the 'nav-open' class from the body to close navigation menu
    window.location.href = '/logout'; // Redirect the user to the logout page
}

// Event listener to toggle navigation menu visibility and reset the timeout
navToggle.addEventListener('click', () => {
    document.body.classList.toggle('nav-open'); // Toggle the 'nav-open' class on the body to show/hide navigation menu
    resetTimeout(); // Reset the inactivity timeout
});

// Event listeners to close navigation menu when a link is clicked and reset the timeout
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        document.body.classList.remove('nav-open'); // Remove the 'nav-open' class from the body to close navigation menu
        resetTimeout(); // Reset the inactivity timeout
    });
});

resetTimeout(); // Call the resetTimeout function when the page loads
