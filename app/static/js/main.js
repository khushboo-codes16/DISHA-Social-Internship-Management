// Notification System
document.addEventListener('DOMContentLoaded', function() {
    // Notification toggle
    const notificationIcon = document.getElementById('notificationIcon');
    const notificationPanel = document.getElementById('notificationPanel');
    const closeNotifications = document.getElementById('closeNotifications');
    const notificationOverlay = document.getElementById('notificationOverlay');
    
    if (notificationIcon) {
        notificationIcon.addEventListener('click', () => {
            notificationPanel.classList.add('active');
            notificationOverlay.classList.add('active');
            fetchUnreadNotifications();
        });
    }
    
    if (closeNotifications) {
        closeNotifications.addEventListener('click', () => {
            notificationPanel.classList.remove('active');
            notificationOverlay.classList.remove('active');
        });
    }
    
    if (notificationOverlay) {
        notificationOverlay.addEventListener('click', () => {
            notificationPanel.classList.remove('active');
            notificationOverlay.classList.remove('active');
        });
    }
    
    // Fetch unread notifications
    function fetchUnreadNotifications() {
        fetch('/api/messages')
            .then(response => response.json())
            .then(messages => {
                const unreadMessages = messages.filter(msg => !msg.is_read);
                updateNotificationBadge(unreadMessages.length);
                
                const notificationList = document.querySelector('.notification-list');
                if (notificationList) {
                    notificationList.innerHTML = unreadMessages.map(msg => `
                        <div class="notification-item unread" data-id="${msg.id}">
                            <div class="notification-title">${msg.title}</div>
                            <p>${msg.content.substring(0, 100)}...</p>
                            <div class="notification-time">${new Date(msg.created_at).toLocaleDateString()}</div>
                        </div>
                    `).join('');
                    
                    // Add click event to mark as read
                    document.querySelectorAll('.notification-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const messageId = this.getAttribute('data-id');
                            markAsRead(messageId);
                            this.classList.remove('unread');
                        });
                    });
                }
            });
    }
    
    function updateNotificationBadge(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    }
    
    function markAsRead(messageId) {
        fetch(`/api/messages/${messageId}/read`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchUnreadNotifications();
                }
            });
    }
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('border-red-500');
                } else {
                    field.classList.remove('border-red-500');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Image preview for file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = this.parentNode.querySelector('.image-preview');
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" class="max-w-full h-auto rounded">`;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});