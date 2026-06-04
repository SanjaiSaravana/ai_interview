/**
 * main.js - Handles the Landing Page logic
 */

function startInterview() {
    const roleSelect = document.getElementById('roleSelect');
    if (!roleSelect) return;

    const selectedRole = roleSelect.value;
    
    // Check if role is empty
    if (!selectedRole) {
        alert("Please select a role before starting.");
        return;
    }

    // Redirect to interview page with the role as a query parameter
    window.location.href = `/interview?role=${encodeURIComponent(selectedRole)}`;
}

// Simple animation for the landing page cards
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        setTimeout(() => {
            container.style.transition = 'all 0.6s ease-out';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }
});