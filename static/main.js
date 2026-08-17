/* ShopEase Main JavaScript */
$(document).ready(function () {

    // ─── Navbar scroll effect ───
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 50) {
            $('#mainNavbar').addClass('scrolled').css('background', 'rgba(13, 13, 26, 0.98)');
        } else {
            $('#mainNavbar').removeClass('scrolled').css('background', 'rgba(13, 13, 26, 0.92)');
        }
    });

    // ─── Auto-hide alerts ───
    setTimeout(function () {
        $('.alert:not(.alert-warning)').fadeOut('slow');
    }, 5000);

    // ─── Add to cart animation ───
    $('[id^="addToCartBtn"]').on('click', function () {
        var btn = $(this);
        var original = btn.html();
        btn.html('<i class="bi bi-check-lg me-2"></i>Added!').prop('disabled', true);
        setTimeout(function () {
            btn.html(original).prop('disabled', false);
        }, 1500);
    });

    // ─── Quantity input validation ───
    $('input[type="number"]').on('change', function () {
        var val = parseInt($(this).val());
        var min = parseInt($(this).attr('min')) || 1;
        var max = parseInt($(this).attr('max')) || 9999;
        if (isNaN(val) || val < min) $(this).val(min);
        if (val > max) $(this).val(max);
    });

    // ─── Product card hover glow ───
    $('.product-card').on('mouseenter', function () {
        $(this).css('box-shadow', '0 16px 48px rgba(108, 99, 255, 0.25)');
    }).on('mouseleave', function () {
        $(this).css('box-shadow', '');
    });

    // ─── Smooth scroll to reviews ───
    $('a[href="#reviews"]').on('click', function (e) {
        e.preventDefault();
        var reviewTab = $('#productTabs button[data-bs-target="#reviewTab"]');
        if (reviewTab.length) {
            reviewTab.trigger('click');
            $('html, body').animate({ scrollTop: $('#productTabs').offset().top - 80 }, 400);
        }
    });

    // ─── Back to top button ───
    var backToTop = $('<button class="back-to-top" title="Back to top"><i class="bi bi-arrow-up"></i></button>');
    $('body').append(backToTop);
    backToTop.css({
        position: 'fixed', bottom: '24px', right: '24px', zIndex: 999,
        width: '44px', height: '44px', borderRadius: '50%',
        background: 'var(--accent)', color: 'white', border: 'none',
        fontSize: '1.1rem', cursor: 'pointer', display: 'none',
        boxShadow: '0 4px 16px rgba(108, 99, 255, 0.4)',
        transition: 'all 0.3s ease'
    });
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 300) {
            backToTop.fadeIn(300);
        } else {
            backToTop.fadeOut(300);
        }
    });
    backToTop.on('click', function () {
        $('html, body').animate({ scrollTop: 0 }, 400);
    });

    // ─── Form submit loading state ───
    $('form').on('submit', function () {
        var btn = $(this).find('[type="submit"]');
        if (btn.length && !btn.data('no-loading')) {
            btn.prop('disabled', true);
            if (!btn.hasClass('pay-btn')) {
                btn.prepend('<span class="spinner-border spinner-border-sm me-2" role="status"></span>');
            }
        }
    });

    // ─── Image lazy load fallback ───
    $('img').on('error', function () {
        $(this).hide();
        $(this).parent().addClass('product-img-placeholder').html('<i class="bi bi-image text-muted fs-1"></i>');
    });

    // ─── Price filter quick buttons ───
    $('.price-quick-btn').on('click', function () {
        var min = $(this).data('min');
        var max = $(this).data('max');
        $('input[name="min_price"]').val(min);
        $('input[name="max_price"]').val(max);
        $('#price-filter-form').submit();
    });

    // ─── Cart count badge update ───
    function updateCartBadge(count) {
        var badge = $('#cart-badge');
        if (count > 0) {
            if (badge.length) {
                badge.text(count);
            } else {
                $('.cart-icon').append('<span class="cart-badge" id="cart-badge">' + count + '</span>');
            }
        } else {
            badge.remove();
        }
    }

    console.log('%cShopEase 🛍️ — Premium Shopping Experience', 'color: #6C63FF; font-size: 14px; font-weight: bold;');
});
