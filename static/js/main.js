/**
 * WiduxBot Admin Panel JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add confirmation to delete actions
    const deleteButtons = document.querySelectorAll('button[type="submit"].btn-danger');
    deleteButtons.forEach(button => {
        if (!button.hasAttribute('data-confirm-set')) {
            button.addEventListener('click', function(event) {
                if (!confirm('هل أنت متأكد من إجراء هذا الحذف؟')) {
                    event.preventDefault();
                }
            });
            button.setAttribute('data-confirm-set', 'true');
        }
    });

    // Handle file upload previews
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            const fileName = event.target.files[0]?.name;
            if (fileName) {
                // Find nearest label or create one
                let label = input.nextElementSibling;
                if (!label || !label.classList.contains('file-name')) {
                    label = document.createElement('small');
                    label.classList.add('file-name', 'text-muted', 'd-block', 'mt-1');
                    input.parentNode.insertBefore(label, input.nextSibling);
                }
                label.textContent = `تم اختيار: ${fileName}`;
            }
        });
    });
});
