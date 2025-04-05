// Main JavaScript file for the Waj Bot web interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Copy Twitch OAuth link to clipboard
    const copyLinkBtn = document.getElementById('copy-oauth-link');
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function() {
            const linkText = document.getElementById('oauth-link').textContent;
            navigator.clipboard.writeText(linkText).then(function() {
                // Change button text temporarily
                const originalText = copyLinkBtn.innerHTML;
                copyLinkBtn.innerHTML = '<i class="fas fa-check"></i> تم النسخ!';
                setTimeout(function() {
                    copyLinkBtn.innerHTML = originalText;
                }, 2000);
            });
        });
    }

    // Channel add form validation
    const addChannelForm = document.getElementById('add-channel-form');
    if (addChannelForm) {
        addChannelForm.addEventListener('submit', function(event) {
            const channelInput = document.getElementById('channel');
            if (!channelInput.value.trim()) {
                event.preventDefault();
                alert('الرجاء إدخال اسم القناة.');
            }
        });
    }

    // Confirm channel removal
    const removeChannelButtons = document.querySelectorAll('.remove-channel-btn');
    removeChannelButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('هل أنت متأكد من حذف هذه القناة؟')) {
                event.preventDefault();
            }
        });
    });

    // Game mode selection
    const gameModeCards = document.querySelectorAll('.game-mode-card');
    gameModeCards.forEach(function(card) {
        card.addEventListener('click', function() {
            // Remove active class from all cards
            gameModeCards.forEach(c => c.classList.remove('border-primary'));
            // Add active class to clicked card
            this.classList.add('border-primary');
            
            // Update hidden input with selected mode
            const modeInput = document.getElementById('selected-mode');
            if (modeInput) {
                modeInput.value = this.dataset.mode;
            }
        });
    });

    // Preview custom messages
    const messageInputs = document.querySelectorAll('.custom-message-input');
    messageInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const previewId = this.dataset.preview;
            const previewElement = document.getElementById(previewId);
            if (previewElement) {
                previewElement.textContent = this.value;
            }
        });
    });

    // Bot status check
    function checkBotStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('bot-status');
                if (statusElement) {
                    if (data.status === 'online') {
                        statusElement.innerHTML = '<span class="badge bg-success">متصل</span>';
                    } else {
                        statusElement.innerHTML = '<span class="badge bg-danger">غير متصل</span>';
                    }
                    
                    // Update channel count if available
                    const channelCountElement = document.getElementById('channel-count');
                    if (channelCountElement && data.active_channels) {
                        channelCountElement.textContent = data.active_channels.length;
                    }
                }
            })
            .catch(error => {
                console.error('Error checking bot status:', error);
                const statusElement = document.getElementById('bot-status');
                if (statusElement) {
                    statusElement.innerHTML = '<span class="badge bg-warning">غير معروف</span>';
                }
            });
    }

    // Check bot status initially and then every 30 seconds
    if (document.getElementById('bot-status')) {
        checkBotStatus();
        setInterval(checkBotStatus, 30000);
    }

    // Toggle password visibility
    const togglePasswordBtn = document.getElementById('toggle-password');
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const passwordInput = document.getElementById('token-input');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Animated counters for statistics
    function animateCounter(element, target) {
        let current = 0;
        const increment = target / 100;
        const duration = 1000; // 1 second
        const interval = duration / 100;
        
        const timer = setInterval(function() {
            current += increment;
            element.textContent = Math.round(current);
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            }
        }, interval);
    }

    // Animate counters when they come into view
    const counterElements = document.querySelectorAll('.counter');
    if (counterElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.getAttribute('data-target'));
                    animateCounter(entry.target, target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        counterElements.forEach(counter => {
            observer.observe(counter);
        });
    }
});
