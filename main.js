// Set current year for copyright in footer
document.addEventListener('DOMContentLoaded', function() {
    const now = new Date();
    const footerYear = document.querySelector('.footer .text-muted');
    if (footerYear) {
        footerYear.innerHTML = footerYear.innerHTML.replace('{{ now.year }}', now.getFullYear());
    }
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        Array.from(tooltips).forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }
    
    // Automatic alert dismissal after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    if (alerts.length > 0) {
        setTimeout(() => {
            Array.from(alerts).forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);
    }
});
