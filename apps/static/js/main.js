// Main JavaScript for JKH CRM

$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('a[data-confirm]').click(function(e) {
        if (!confirm($(this).data('confirm'))) {
            e.preventDefault();
            return false;
        }
    });

    // Auto-hide success messages
    $('.alert-success').delay(3000).fadeOut('slow');

    // Form validation
    $('form').submit(function() {
        $(this).find('button[type="submit"]').prop('disabled', true);
        $(this).find('button[type="submit"]').html('<i class="bi bi-hourglass-split"></i> Обработка...');
    });

    // Scroll to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#scrollToTop').fadeIn();
        } else {
            $('#scrollToTop').fadeOut();
        }
    });

    $('#scrollToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 800);
        return false;
    });

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
});

// Format date and time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Number formatting
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}