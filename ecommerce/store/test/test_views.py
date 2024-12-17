from django.test import TestCase, Client
from django.contrib.auth.models import User
from store.models import Customer, Product, Order, OrderItem, ShippingConfig
from django.test.client import RequestFactory
from store.views import cartData
import json

class StoreViewsTestCase(TestCase):

    def setUp(self):
        """
        Tesztadatok létrehozása
        """
        self.client = Client()

        # Felhasználó létrehozása, ha még nem létezik
        self.user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'test1234!'})

        # Customer létrehozása, ha még nem létezik
        self.customer, created = Customer.objects.get_or_create(user=self.user)

        # Termékek létrehozása
        self.product1 = Product.objects.create(name="Termék1", price=1000)
        self.product2 = Product.objects.create(name="Termék2", price=2000)

        # Rendelés létrehozása
        self.order = Order.objects.create(customer=self.customer, complete=False)

        # Rendelési tétel létrehozása
        self.order_item1 = OrderItem.objects.create(order=self.order, product=self.product1, quantity=2)
        self.order_item2 = OrderItem.objects.create(order=self.order, product=self.product2, quantity=1)

        # Szállítási beállítások létrehozása
        self.shipping_config = ShippingConfig.objects.create(shipping_cost=500, free_shipping_threshold=5000)

        # A teszt kéréshez RequestFactory szükséges
        self.factory = RequestFactory()

    def test_cartData_authenticated_user(self):
        """
        Teszteljük a `cartData` függvényt bejelentkezett felhasználóval.
        """
        # Bejelentkezés
        self.client.login(username='testuser', password='test1234!')

        # Készítsünk egy kérést a cartData függvényhez
        request = self.factory.get('/cart/')  # Itt nem lényeges az URL, csak a request kell
        request.user = self.user  # A teszt során bejelentkezett felhasználó

        # Közvetlenül meghívjuk a cartData függvényt
        context = cartData(request)

        # Ellenőrizzük, hogy a kosár tételek és a végösszeg helyesen jelennek meg
        self.assertEqual(context['cartItems'], 3)  # 3 tétel (2 termék1, 1 termék2)
        self.assertEqual(context['cart_total'], 4500)  # 1000*2 + 2000*1 = 4000
        self.assertEqual(len(context['items']), 2)  # 2 rendelési tétel (2 termék1 és 1 termék2)



    def test_processOrder_authenticated_user(self):
        """
        Teszteljük a `processOrder` nézetet bejelentkezett felhasználóval
        """
        
        # Ellenőrizd, hogy létezik a tesztfelhasználó
        user = User.objects.create_user(username='testuser1', password='test1234!')
        
        # Bejelentkezés a tesztfelhasználóval
        self.client.login(username='testuser1', password='test1234!')

        # Tesztadatok
        data = {
            'shipping':{
                'address': 'Teszt utca 1.',
                'city': 'Tesztváros',
                'street_number': '12',
                'zipcode': '1234'
            },
        }

        # Kérés küldése
        response = self.client.post('/process_order/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.filter(complete=True).count(), 1)  # Rendelés befejezve




    def test_updateItem_add(self):
        """
        Teszteljük az `updateItem` nézetet
        """
        # Ellenőrizd, hogy létezik a tesztfelhasználó
        user = User.objects.create_user(username='testuser2', password='test1234!')

        self.client.login(username='testuser2', password='test1234!')

        data = {
            'productId': self.product2.id,
            'action': 'add',
            'quantity': 1
        }
        response = self.client.post('/update_item/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Ellenőrizzük az OrderItem frissítését
        order_item = OrderItem.objects.get(order=self.order, product=self.product2)
        self.assertEqual(order_item.quantity, 1)


