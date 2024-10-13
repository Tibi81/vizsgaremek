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
    #digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(blank=True)  # Új mező a leíráshoz
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='option1')  # Legördülő menü mező

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

    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vásárló")
    date_order = models.DateTimeField(auto_now_add=True, verbose_name="Rendelés dátuma")
    complete = models.BooleanField(default=False, verbose_name="Befejezett")
    transaction_id = models.CharField(max_length=100, null=True, verbose_name="Tranzakció azonosító")

    class Meta:
        verbose_name = "Rendelés"
        verbose_name_plural = "Rendelések"

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
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
        if self.product and self.product.price is not None:
            return self.product.price * self.quantity
        return 0  # Visszatér 0, ha a termék nincs vagy a price null     

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
    