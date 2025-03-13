document.addEventListener("DOMContentLoaded", function () {
    const checkoutBtn = document.querySelector(".cart-checkout-btn");
    
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent immediate navigation

            const cartWrapper = document.querySelector(".cart-wrapper");

            if (cartWrapper) {
                // Apply exit animation
                cartWrapper.classList.add("slide-out");

                // Delay navigation until animation completes
                setTimeout(() => {
                    window.location.href = checkoutBtn.href; // Navigate to checkout
                }, 500); // Match animation duration
            }
        });
    }
});
