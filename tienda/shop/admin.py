from django.contrib import admin
from .models import Product, Order, OrderItem, ContactMessage, Category

# Register your models here.

admin.site.register(Product)
admin.site.register(ContactMessage)

# INLINE
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
# ADMIN DE ORDER
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
# REGISTRO FINAL
admin.site.register(Order, OrderAdmin)

admin.site.register(Category)
