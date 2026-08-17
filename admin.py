from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Wishlist, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'image_tag']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'name', 'slug', 'short_description', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'discount_price', 'stock')}),
        ('Images', {'fields': ('image', 'image_preview', 'image2', 'image3')}),
        ('Visibility', {'fields': ('is_active', 'is_featured')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:4px;" />', obj.image.url)
        return '—'
    image_tag.short_description = 'Image'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="border-radius:8px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']

    def total_price(self, obj):
        return f"₹{obj.total_price}"
    total_price.short_description = 'Total'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'total_items', 'subtotal', 'created_at']
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Items'

    def subtotal(self, obj):
        return f"₹{obj.subtotal}"
    subtotal.short_description = 'Subtotal'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

    def total_price(self, obj):
        return f"₹{obj.total_price}"
    total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method', 'payment_id', 'razorpay_order_id')}),
        ('Customer Details', {'fields': ('full_name', 'email', 'phone')}),
        ('Shipping Address', {'fields': ('address', 'city', 'state', 'pincode', 'country')}),
        ('Pricing', {'fields': ('subtotal', 'shipping_cost', 'total_price')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
