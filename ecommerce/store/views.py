from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime

from .models import Customer, Product, Order, OrderItem, ShippingAddress

from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .forms import CustomUserCreationForm


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        cartItems = 0
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}  # Üres kosár nem bejelentkezett felhasználóknál
    return {'cartItems': cartItems, 'order': order, 'items': items}


class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()
        # A termékek lekérdezése, egyszerű lista létrehozása a termékekből
        product_list = [{'id': product.id, 'name': product.name, 'price': product.price} for product in products]
        return Response(product_list)

    def post(self, request):
        # Itt kézzel kell létrehoznod a terméket
        product_data = request.data
        product = Product(name=product_data['name'], price=product_data['price'])
        product.save()
        return Response({'id': product.id, 'name': product.name, 'price': product.price}, status=status.HTTP_201_CREATED)
    

from django.contrib.auth.views import LoginView
from .models import Order

class CustomLoginView(LoginView):
    template_name = 'store/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartItems = 0  # Alapértelmezett kosár tartalom

        if self.request.user.is_authenticated:
            customer = getattr(self.request.user, 'customer', None)
            # Csak bejelentkezett felhasználók esetén kérdezzük le a kosár tartalmát
            if customer:
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                cartItems = order.get_cart_items

        context['cartItems'] = cartItems
        return context

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.complete = True
        order.transaction_id = transaction_id
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
        
        return JsonResponse('Order processed successfully', safe=False)
    else:
        return JsonResponse({'message': 'A rendelés feldolgozásához be kell jelentkezni!'}, status=401)
    
def updateItem(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'A rendeléshez be kell jelentkeznie!'}, status=401)

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def cart(request):
    data = cartData(request)
    context = {'items': data['items'], 'order': data['order'], 'cartItems': data['cartItems']}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    context = {'items': data['items'], 'order': data['order'], 'cartItems': data['cartItems']}
    return render(request, 'store/checkout.html', context)

def filtered_products(request):
    filter_option = request.GET.get('filter')
    print(f"Filter option: {filter_option}")  # Debug üzenet

    category_map = {
        'FÁB': 'option1',
        'kotott': 'option2',
        'pottos': 'option3',
        'textil': 'option4',
    }
    filter_option = category_map.get(filter_option, None)
    print(f"Mapped filter option: {filter_option}")  # Debug üzenet

    if filter_option:
        products = Product.objects.filter(category=filter_option)
        print(f"Filtered products: {products}")  # Debug üzenet
        if not products.exists():
            message = "Nincs ilyen termék a megadott kategóriában."
        else:
            message = ""
    else:
        products = Product.objects.all()
        message = ""

    # Kosár kezelés a cartData függvény használatával
    cart_info = cartData(request)  # Hívjuk meg a cartData függvényt
    items = cart_info['items']  # Kosár elemek
    order = cart_info['order']  # Kosár adatok
    cartItems = cart_info['cartItems']  # Kosár elemek száma

    context = {
        'products': products,
        'items': items,  # Kosár elemek
        'order': order,  # Kosár adatok
        'cartItems': cartItems,  # Kosárban lévő elemek száma
        'message': message  # Üzenet a szűrésről
    }

    return render(request, 'store/filtered_products.html', context)







def order_list(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        
        # Befejezett rendelések lekérdezése
        #completed_orders = Order.objects.filter(customer=customer, complete=True).prefetch_related('orderitem_set')
        # Befejezett rendelések lekérdezése időrendben csökkenő sorrendben
        completed_orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_order').prefetch_related('orderitem_set')


        # Kosár adatok lekérdezése a cartData függvényből
        cart_data = cartData(request)
        cart_items_count = cart_data['cartItems']
        cart_items = cart_data['items']

        # Rendelések csoportosítása transaction_id alapján
        orders_by_transaction = {}
        for order in completed_orders:
            transaction_id = order.transaction_id
            if transaction_id not in orders_by_transaction:
                orders_by_transaction[transaction_id] = []
            orders_by_transaction[transaction_id].append(order)

          # Összeadás minden rendelési tételhez
            for order_item in order.orderitem_set.all():
                order_item.total_price = order_item.product.price * order_item.quantity    
            

         

        context = {
            'orders_by_transaction': orders_by_transaction,
            'cartItems': cart_items_count,
            'cart_items': cart_items,  # Az aktuális kosár tételei a kontextusban
        }
    else:
        # Csak bejelentkezett felhasználóknak üzenet
        context = {
            'message': 'Csak bejelentkezett felhasználóknak!',
            'cartItems': 0,
            'cart_items': []  # Üres kosár nem bejelentkezett felhasználóknál
        }

    return render(request, 'store/order_list.html', context)






def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Kosár adatok lekérdezése a cartData függvényből
    cart_data = cartData(request)  # Kosár adatok lekérdezése
    cartItems = cart_data['cartItems']  # Kosár tételek száma
    items = cart_data['items']  # Kosár tételek

    # Megjelenítjük a kosarat, ha a felhasználó be van jelentkezve
    show_cart = request.user.is_authenticated

    context = {
        'product': product,
        'items': items,
        'cartItems': cartItems,
        'show_cart': show_cart
    }
    return render(request, 'store/product_detail.html', context)



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Fiókja létrejött! Most már bejelentkezhet.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    # Kosár adatok lekérdezése a cartData függvényből
    cart_data = cartData(request)  # Kosár adatok lekérdezése
    cartItems = cart_data['cartItems']  # Kosár tételek száma

    context = {'form': form, 'cartItems': cartItems}
    return render(request, 'store/register.html', context)


def store(request):
    cart_data = cartData(request)  # Kosár adatok lekérdezése a cartData függvényből
    cartItems = cart_data['cartItems']
    items = cart_data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'items': items}
    return render(request, 'store/store.html', context)


def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query)

    # Kosár adatok lekérdezése a cartData függvényből
    cart_data = cartData(request)  # Kosár adatok lekérdezése
    cartItems = cart_data['cartItems']  # Kosár tételek száma
    items = cart_data['items']  # Kosár tételek

    context = {
        'products': products,
        'items': items,
        'cartItems': cartItems,
    }

    return render(request, 'store/search_results.html', context)