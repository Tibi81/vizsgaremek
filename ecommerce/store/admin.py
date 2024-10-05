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

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_order', 'complete', 'transaction_id', 'get_order_summary')  # Hozzáadjuk az összegzőt


