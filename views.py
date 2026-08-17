from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator

from .models import Category, Product, Cart, CartItem, Order, OrderItem, Wishlist, ProductReview
from .forms import CheckoutForm, SearchForm, ReviewForm


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge guest cart on login
        if request.session.session_key:
            guest_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if guest_cart and guest_cart != cart:
                for item in guest_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        cart_item.quantity += item.quantity
                    else:
                        cart_item.quantity = item.quantity
                    cart_item.save()
                guest_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# ─────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────

class HomeView(View):
    template_name = 'shop/home.html'

    def get(self, request):
        featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8]
        latest_products = Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')[:8]
        categories = Category.objects.filter(is_active=True)
        search_form = SearchForm()
        return render(request, self.template_name, {
            'featured_products': featured_products,
            'latest_products': latest_products,
            'categories': categories,
            'search_form': search_form,
        })


# ─────────────────────────────────────────────
# Product Listing
# ─────────────────────────────────────────────

class ProductListView(View):
    template_name = 'shop/product_list.html'

    def get(self, request, category_slug=None):
        products = Product.objects.filter(is_active=True).select_related('category')
        categories = Category.objects.filter(is_active=True)
        current_category = None
        search_query = request.GET.get('q', '')
        sort_by = request.GET.get('sort', '-created_at')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
            products = products.filter(category=current_category)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass

        sort_options = {
            '-created_at': 'Newest First',
            'price': 'Price: Low to High',
            '-price': 'Price: High to Low',
            'name': 'Name A-Z',
        }
        if sort_by in sort_options:
            products = products.order_by(sort_by)

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'products': page_obj,
            'categories': categories,
            'current_category': current_category,
            'search_query': search_query,
            'sort_by': sort_by,
            'sort_options': sort_options,
            'min_price': min_price,
            'max_price': max_price,
            'search_form': SearchForm(initial={'q': search_query}),
        })


# ─────────────────────────────────────────────
# Product Detail
# ─────────────────────────────────────────────

class ProductDetailView(View):
    template_name = 'shop/product_detail.html'

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        related_products = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk)[:4]
        reviews = product.reviews.select_related('user').all()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        review_form = ReviewForm()
        in_wishlist = False
        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

        return render(request, self.template_name, {
            'product': product,
            'related_products': related_products,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_form': review_form,
            'in_wishlist': in_wishlist,
        })

    def post(self, request, slug):
        """Handle review submission."""
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to write a review.')
            return redirect('accounts:login')
        product = get_object_or_404(Product, slug=slug, is_active=True)
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, 'You have already reviewed this product.')
            return redirect('shop:product_detail', slug=slug)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
        return redirect('shop:product_detail', slug=slug)


# ─────────────────────────────────────────────
# Cart
# ─────────────────────────────────────────────

class CartView(View):
    template_name = 'shop/cart.html'

    def get(self, request):
        cart = get_or_create_cart(request)
        cart_items = cart.items.select_related('product').all()
        return render(request, self.template_name, {
            'cart': cart,
            'cart_items': cart_items,
        })


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        if not product.in_stock:
            messages.error(request, f'"{product.name}" is out of stock.')
            return redirect(request.META.get('HTTP_REFERER', 'shop:home'))
        quantity = int(request.POST.get('quantity', 1))
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'"{product.name}" added to cart!')
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('shop:cart')


class UpdateCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, pk=item_id)
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        return redirect('shop:cart')


class RemoveFromCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, pk=item_id)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f'"{product_name}" removed from cart.')
        return redirect('shop:cart')


class ClearCartView(View):
    def post(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        messages.info(request, 'Cart cleared.')
        return redirect('shop:cart')


# ─────────────────────────────────────────────
# Checkout
# ─────────────────────────────────────────────

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'shop/checkout.html'

    def get(self, request):
        cart = get_or_create_cart(request)
        if cart.total_items == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('shop:cart')
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        })
        return render(request, self.template_name, {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'form': form,
        })

    def post(self, request):
        cart = get_or_create_cart(request)
        if cart.total_items == 0:
            return redirect('shop:cart')
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.subtotal
            order.shipping_cost = 0 if cart.subtotal >= 500 else 50
            order.total_price = order.subtotal + order.shipping_cost
            order.save()

            # Create order items from cart
            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.effective_price,
                    quantity=item.quantity,
                )
                # Reduce stock
                item.product.stock -= item.quantity
                item.product.save()

            # Store order ID in session for payment
            request.session['pending_order_id'] = order.id

            # Redirect to payment
            return redirect('payments:payment', order_id=order.id)
        return render(request, self.template_name, {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'form': form,
        })


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────

class OrderSuccessView(LoginRequiredMixin, View):
    template_name = 'shop/order_success.html'

    def get(self, request):
        order_number = request.session.get('last_order_number')
        order = None
        if order_number:
            order = Order.objects.filter(order_number=order_number, user=request.user).first()
        return render(request, self.template_name, {'order': order})


class OrderHistoryView(LoginRequiredMixin, View):
    template_name = 'shop/order_history.html'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
        return render(request, self.template_name, {'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    template_name = 'shop/order_detail.html'

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, self.template_name, {'order': order})


# ─────────────────────────────────────────────
# Wishlist
# ─────────────────────────────────────────────

class WishlistView(LoginRequiredMixin, View):
    template_name = 'shop/wishlist.html'

    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        return render(request, self.template_name, {'wishlist_items': wishlist_items})


class ToggleWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            messages.info(request, f'"{product.name}" removed from wishlist.')
        else:
            messages.success(request, f'"{product.name}" added to wishlist!')
        return redirect(request.META.get('HTTP_REFERER', 'shop:wishlist'))
