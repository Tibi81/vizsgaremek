from django.contrib import admin


# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')  # Itt távolítsd el az 'action_checkbox'-t

    def get_queryset(self, request):
        # Itt felülírjuk az alapértelmezett querysetet, és hozzácsatoljuk a felhasználói adatokat
        qs = super().get_queryset(request)
        return qs.select_related('user')  # A kapcsolódó user mezőt gyorsabban tölti be

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)



class OrderItemInline(admin.TabularInline):  # Változtasd meg StackInline-ról TabularInline-re
    model = OrderItem
    extra = 0  # Hány üres sort szeretnél megjeleníteni
    fields = ('product', 'quantity', 'get_total')  # Csak olvasható mezők
    readonly_fields = ('get_total',)  # Mely mezőket szeretnéd látni


from django.utils.html import format_html

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'customer', 'date_order', 'complete', 'transaction_id', 'display_products', 'display_quantities', 'display_shipping_address' )
    search_fields = ['customer__username', 'transaction_id']

    def display_products(self, obj):
        return format_html("<br>".join([str(item.product) for item in obj.orderitem_set.all()]))
    display_products.short_description = 'Termékek'

    def display_quantities(self, obj):
        return format_html("<br>".join([str(item.quantity) for item in obj.orderitem_set.all()]))
    display_quantities.short_description = 'Mennyiségek'

    def display_shipping_address(self, obj):
        shipping_address = ShippingAddress.objects.filter(order=obj).first()
        if shipping_address:
            return format_html(f"{shipping_address.zipcode}<br>{shipping_address.city}<br>{shipping_address.address}<br>{shipping_address.street_number}<br>")
        return "No shipping address"
    display_shipping_address.short_description = 'Szállítási cím'




'''
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_order', 'complete', 'transaction_id', 'get_order_summary')  # Hozzáadjuk az összegzőt
'''

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)