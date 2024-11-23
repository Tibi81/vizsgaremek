from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200)
    class Meta:
        verbose_name = "Vásárló"
        verbose_name_plural = "Vásárlók"

    def __str__(self):
        return self.name if self.name else "névtelen ügyfél"  # Vagy bármilyen más alapértelmezett string


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('option1', 'FÁBÓL KÉSZÜLT'),
        ('option2', 'KÖTÖTT-HORGOLT'),
        ('option3', 'PÖTTYÖSCICA'),
        ('option4', 'TEXTIL'),
    ]

    name = models.CharField(max_length=200)
    price = models.FloatField()
    discount_percentage = models.FloatField(default=0)  # Kedvezmény százalék mező
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='option1')

    class Meta:
        verbose_name = "Termék"
        verbose_name_plural = "Termékek"

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def discounted_price(self):
        """Kiszámítja az akciós árat a kedvezmény százalék alapján."""
        if self.discount_percentage > 0:
            discount_amount = (self.discount_percentage / 100) * self.price
            return round(self.price - discount_amount, 2)
        return self.price

import math   
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vásárló")
    date_order = models.DateTimeField(auto_now_add=True, verbose_name="Rendelés dátuma")
    complete = models.BooleanField(default=False, verbose_name="Befejezett")
    transaction_id = models.CharField(max_length=100, null=True, verbose_name="Tranzakció azonosító")
    discount_percentage = models.FloatField(default=0) 

    class Meta:
        verbose_name = "Rendelés"
        verbose_name_plural = "Rendelések"

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        discount_amount = (self.discount_percentage / 100) * total
        return total - discount_amount  # Kedvezménnyel csökkentett összeg
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 
    
    @property
    def get_order_summary(self):
        order_items = self.orderitem_set.all()
        summary = []
        for item in order_items:
            summary.append(f"{item.product.name} (x{item.quantity})")  # Termék név és mennyiség
        return ", ".join(summary)  # Összesített szöveg
    
    def get_item_names(self):
        return ", ".join([f"{item.product.name}" for item in self.orderitem_set.all()])

    def get_item_quantities(self):
        return ", ".join([f"{item.quantity}" for item in self.orderitem_set.all()])

    def get_item_prices(self):
        return ", ".join([f"{item.product.price} Ft" for item in self.orderitem_set.all()])
        

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rendelési tétel"
        verbose_name_plural = "Rendelési tételek"

    @property
    def get_total(self):
        if self.product and self.product.discounted_price is not None:
            return self.product.discounted_price * self.quantity  # Az akciós ár használata
        return self.product.price * self.quantity  # Ha nincs akciós ár, az alapár használata
  

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    street_number = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Szállítási cím"
        verbose_name_plural = "Szállítási címek"
    

    def __str__(self):
        return self.address
    
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Review(models.Model):
    RATING_CHOICES = [(i) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]  # Csak 1 és 5 közötti értékek engedélyezettek
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vélemény"
        verbose_name_plural = "Vélemények"
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.name} - {self.rating}'
    


class TopBarText(models.Model):
    title = models.CharField(max_length=100, verbose_name="Cím")
    content = models.TextField(verbose_name="Szöveg")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Utolsó frissítés")

    def __str__(self):
        return self.title

    



