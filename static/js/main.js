// Enhanced script for WiduxBot webapp
document.addEventListener("DOMContentLoaded", function() {
    // Set current year for copyright in footer
    const now = new Date();
    const footerYear = document.querySelector(".footer .text-muted");
    if (footerYear) {
        footerYear.innerHTML = footerYear.innerHTML.replace("{{ now.year }}", now.getFullYear());
    }
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll("[data-bs-toggle=\"tooltip\"]");
    if (tooltips.length > 0) {
        Array.from(tooltips).forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }
    
    // Automatic alert dismissal after 5 seconds
    const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
    if (alerts.length > 0) {
        setTimeout(() => {
            Array.from(alerts).forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);
    }

    // Toggle channel status
    const toggleButtons = document.querySelectorAll(".toggle-channel-btn");
    toggleButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            const channelId = this.getAttribute("data-channel-id");
            const statusBadge = document.querySelector(`#channel-${channelId} .channel-status`);
            const spinner = this.querySelector(".spinner-border");
            const buttonText = this.querySelector(".btn-text");
            
            // Show loading state
            if (spinner) spinner.classList.remove("d-none");
            if (buttonText) buttonText.textContent = "جاري التحديث...";
            
            // Send request to toggle status
            fetch(`/toggle/${channelId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update UI based on new status
                if (data.success) {
                    if (data.is_active) {
                        statusBadge.textContent = "نشط";
                        statusBadge.classList.remove("bg-secondary");
                        statusBadge.classList.add("bg-success");
                        this.textContent = "إيقاف";
                        this.classList.remove("btn-success");
                        this.classList.add("btn-danger");
                    } else {
                        statusBadge.textContent = "متوقف";
                        statusBadge.classList.remove("bg-success");
                        statusBadge.classList.add("bg-secondary");
                        this.textContent = "تشغيل";
                        this.classList.remove("btn-danger");
                        this.classList.add("btn-success");
                    }
                } else {
                    // Show error
                    const alertContainer = document.querySelector(".container > .alert-container");
                    if (alertContainer) {
                        const alert = document.createElement("div");
                        alert.className = "alert alert-danger alert-dismissible fade show";
                        alert.innerHTML = `
                            <strong>خطأ!</strong> ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        alertContainer.appendChild(alert);
                        
                        // Auto dismiss after 5 seconds
                        setTimeout(() => {
                            const bsAlert = new bootstrap.Alert(alert);
                            bsAlert.close();
                        }, 5000);
                    }
                }
            })
            .catch(error => console.error("Error:", error))
            .finally(() => {
                // Reset button state
                if (spinner) spinner.classList.add("d-none");
                if (buttonText) buttonText.textContent = statusBadge.textContent === "نشط" ? "إيقاف" : "تشغيل";
            });
        });
    });

    // Form validation for question submission
    const questionForm = document.getElementById("add-question-form");
    if (questionForm) {
        questionForm.addEventListener("submit", function(e) {
            const questionText = document.getElementById("question").value.trim();
            const answers = document.getElementById("answers").value.trim();
            
            if (questionText === "" || answers === "") {
                e.preventDefault();
                const alertContainer = document.querySelector(".question-form-alerts");
                
                if (alertContainer) {
                    alertContainer.innerHTML = `
                        <div class="alert alert-danger alert-dismissible fade show">
                            الرجاء ملء جميع الحقول المطلوبة
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                }
            }
        });
    }
});

