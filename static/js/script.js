document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(
        ".action-card, .impact-card"
    );

    cards.forEach((card, index) => {
        card.style.animation = `fadeIn 0.6s ease ${index * 0.1}s both`;
    });
});