/* LearnSwedish Platform Main JavaScript Helpers */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Flashcard flip helper
function flipCard(cardElement) {
    cardElement.classList.toggle('flipped');
}

// Tab navigation helper
function switchTab(tabGroup, tabId) {
    const groupContainer = document.getElementById(tabGroup);
    if (!groupContainer) return;

    const tabs = groupContainer.querySelectorAll('.tab-btn');
    const contents = groupContainer.querySelectorAll('.tab-content');

    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));

    const targetTab = groupContainer.querySelector(`[data-tab="${tabId}"]`);
    const targetContent = document.getElementById(tabId);

    if (targetTab) targetTab.classList.add('active');
    if (targetContent) targetContent.classList.add('active');
}
