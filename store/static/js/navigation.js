document.addEventListener("DOMContentLoaded", function () {
    let dots = document.querySelectorAll(".dots span");

    // Reset all dots
    function resetDots() {
        dots.forEach(dot => dot.classList.remove("active-dot"));
    }

    // Get the current page URL
    let path = window.location.pathname;

    // Reset dots before applying the active class
    resetDots();

    // Apply active class based on page
    if (path.includes("login")) {
        dots[0].classList.add("active-dot");  // First dot for login
    } else if (path.includes("signup")) {
        dots[1].classList.add("active-dot");  // Second dot for signup
    } else if (path.includes("password_reset")) {
        dots[2].classList.add("active-dot");  // Third dot for password reset
    }
});
