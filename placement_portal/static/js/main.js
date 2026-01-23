// =============================================================================
// FILE: main.js
// PURPOSE: Custom JavaScript for Placement Portal application
// DESCRIPTION: Client-side interactivity and enhancements
// =============================================================================

// Wait for DOM to be fully loaded before executing scripts
document.addEventListener('DOMContentLoaded', function() {
    
    // =============================================================================
    // AUTO-DISMISS ALERTS
    // =============================================================================
    
    // Get all alert elements that should auto-dismiss
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    // Loop through alerts and set timeout for auto-dismissal
    alerts.forEach(function(alert) {
        // timeout_duration: Auto-dismiss after 5 seconds (5000ms)
        setTimeout(function() {
            // Use Bootstrap's alert close functionality
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // =============================================================================
    // FORM VALIDATION
    // =============================================================================
    
    // Get all forms that need custom validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop through forms and prevent submission if invalid
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // Check if form is valid
            if (!form.checkValidity()) {
                // Prevent form submission
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Add validation classes to show feedback
            form.classList.add('was-validated');
        }, false);
    });
    
    // =============================================================================
    // CONFIRMATION DIALOGS
    // =============================================================================
    
    // Get all elements that need confirmation before action
    const confirmLinks = document.querySelectorAll('[data-confirm]');
    
    confirmLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            // Get custom confirmation message or use default
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            
            // Show confirmation dialog
            if (!confirm(message)) {
                // Cancel action if user clicks "Cancel"
                event.preventDefault();
            }
        });
    });
    
    // =============================================================================
    // TOOLTIPS INITIALIZATION
    // =============================================================================
    
    // Initialize all Bootstrap tooltips on the page
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // =============================================================================
    // POPOVERS INITIALIZATION
    // =============================================================================
    
    // Initialize all Bootstrap popovers on the page
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // =============================================================================
    // SMOOTH SCROLL TO TOP
    // =============================================================================
    
    // Create "Back to Top" button dynamically
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle d-none';
    backToTopBtn.id = 'backToTop';
    backToTopBtn.style.zIndex = '1000';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.remove('d-none');
        } else {
            backToTopBtn.classList.add('d-none');
        }
    });
    
    // Scroll to top when button is clicked
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // =============================================================================
    // SEARCH FUNCTIONALITY ENHANCEMENTS
    // =============================================================================
    
    // Get search input if exists
    const searchInput = document.querySelector('input[name="search"]');
    
    if (searchInput) {
        // Clear button functionality
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'btn btn-sm btn-outline-secondary';
        clearBtn.innerHTML = '<i class="bi bi-x"></i>';
        clearBtn.style.display = 'none';
        
        // Show clear button when input has value
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                clearBtn.style.display = 'inline-block';
            } else {
                clearBtn.style.display = 'none';
            }
        });
        
        // Clear input when clear button is clicked
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            clearBtn.style.display = 'none';
            searchInput.focus();
        });
    }
    
    // =============================================================================
    // TABLE SORTING (Simple client-side sorting)
    // =============================================================================
    
    // Get all sortable table headers
    const sortableHeaders = document.querySelectorAll('th[data-sortable]');
    
    sortableHeaders.forEach(function(header) {
        // Make header clickable
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="bi bi-chevron-expand"></i>';
        
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = Array.from(this.parentElement.children).indexOf(this);
            const isAscending = this.classList.contains('asc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.children[column].textContent.trim();
                const bValue = b.children[column].textContent.trim();
                
                if (isAscending) {
                    return aValue > bValue ? 1 : -1;
                } else {
                    return aValue < bValue ? 1 : -1;
                }
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
            
            // Toggle sort direction
            this.classList.toggle('asc');
        });
    });
    
    // =============================================================================
    // LOADING INDICATOR FOR FORMS
    // =============================================================================
    
    // Get all forms that should show loading state
    const loadingForms = document.querySelectorAll('form[data-loading]');
    
    loadingForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // Find submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            
            if (submitBtn && form.checkValidity()) {
                // Disable button and show loading spinner
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                
                // Re-enable after timeout (fallback in case of errors)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000); // 10 seconds timeout
            }
        });
    });
    
    // =============================================================================
    // CHARACTER COUNTER FOR TEXTAREAS
    // =============================================================================
    
    // Get all textareas with maxlength attribute
    const countedTextareas = document.querySelectorAll('textarea[maxlength]');
    
    countedTextareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        
        // Create counter element
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted';
        counter.textContent = `0 / ${maxLength} characters`;
        
        // Insert counter after textarea
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        // Update counter on input
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            counter.textContent = `${currentLength} / ${maxLength} characters`;
            
            // Change color when approaching limit
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    });
    
});

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * showToast - Display Bootstrap toast notification
 * 
 * Shows a temporary toast notification to the user.
 * 
 * @param {string} message - Message to display
 * @param {string} type - Toast type: 'success', 'error', 'info', 'warning'
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastEl);
    
    // Show toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * confirmAction - Show confirmation dialog
 * 
 * Displays a confirmation dialog before performing an action.
 * 
 * @param {string} message - Confirmation message
 * @param {function} callback - Function to execute if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}
