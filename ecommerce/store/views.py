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
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
            order = orders.first()
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        else:
            items = []
            cartItems = 0
            order = {'get_cart_total': 0, 'get_cart_items': 0}  # Üres kosár
    else:
        items = []
        cartItems = 0
        order = {'get_cart_total': 0, 'get_cart_items': 0}  # Üres kosár

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
                orders = Order.objects.filter(customer=customer, complete=False)
                if orders.exists():
                    order = orders.first()
                    cartItems = order.get_cart_items
                else:
                    # Ha nincs létező kosár, ne hozzunk létre újat
                    order = None

        context['cartItems'] = cartItems
        return context

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.complete = True
        order.transaction_id = transaction_id
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            street_number=data['shipping']['street_number'],
            zipcode=data['shipping']['zipcode'],
        )
        
        return JsonResponse('A rendelés feldolgozása sikeresen megtörtént', safe=False)
    
    
    else:
        return JsonResponse({'message': 'A rendelés feldolgozásához be kell jelentkezni!'}, status=401)



import json
from django.http import JsonResponse
from .models import Product, Order, OrderItem

def updateItem(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'A rendeléshez be kell jelentkeznie!'}, status=401)

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    quantity = int(data.get('quantity', 1))  # Konvertáld egész számra

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += quantity
    elif action == 'remove':
        orderItem.quantity -= quantity
    elif action == 'delete':
        itemTotal = orderItem.get_total
        orderItem.delete()
        return JsonResponse({'message': 'Item was deleted', 'itemTotal': itemTotal}, safe=False)

    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)






def cart(request):
    data = cartData(request)
    context = {'items': data['items'], 'order': data['order'], 'cartItems': data['cartItems']}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    context = {'items': data['items'], 'order': data['order'], 'cartItems': data['cartItems']}
    return render(request, 'store/checkout.html', context)




from django.core.paginator import Paginator

def filtered_products(request):
    filter_option = request.GET.get('filter', '').lower()
    orderby = request.GET.get('orderby', 'name')  # Alapértelmezett rendezés név szerint
    direction = request.GET.get('direction', 'asc')  # Alapértelmezett sorrend növekvő

    category_map = {
        'fabol': ('option1', 'FÁBÓL KÉSZÜLT'),
        'kotott': ('option2', 'KÖTÖTT-HORGOLT'),
        'pottos': ('option3', 'PÖTTYÖSCICA'),
        'textil': ('option4', 'TEXTIL'),
    }

    if filter_option in category_map:
        products = Product.objects.filter(category=category_map[filter_option][0])
        display_name = category_map[filter_option][1]
    else:
        products = Product.objects.all()
        display_name = "Összes termék"

    if not products.exists():
        message = "Nincs ilyen termék a megadott kategóriában."
    else:
        message = ""

    if orderby:
        direction_prefix = '-' if direction == 'desc' else ''
        products = products.order_by(f"{direction_prefix}{orderby}")
    else:
        products = products.order_by('name')

    cart_info = cartData(request)
    paginator = Paginator(products, 6)  # 6 termék oldalanként
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products': products_page,  # Lapozott oldalak helyesen
        'items': cart_info['items'],
        'order': cart_info['order'],
        'cartItems': cart_info['cartItems'],
        'message': message,
        'filter_option': filter_option,
        'orderby': orderby,
        'direction': direction,
        'display_name': display_name,
    }
    return render(request, 'store/filtered_products.html', context)








def order_list(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        # Befejezett rendelések lekérdezése időrendben csökkenő sorrendben
        completed_orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_order').prefetch_related('orderitem_set')

        # Kosár adatok lekérdezése a cartData függvényből
        cart_data = cartData(request)
        cart_items_count = cart_data['cartItems']
        cart_items = cart_data['items']
        order = cart_data['order']
        products = Product.objects.all()

        # Rendelések csoportosítása transaction_id alapján
        orders_by_transaction = {}
        for order in completed_orders:
            transaction_id = order.transaction_id
            if transaction_id not in orders_by_transaction:
                orders_by_transaction[transaction_id] = []
            orders_by_transaction[transaction_id].append(order)

            # Összeadás minden rendelési tételhez
            for order_item in order.orderitem_set.all():
                if order_item.product:  # Ellenőrizd, hogy a product nem None
                    order_item.total_price = order_item.product.price * order_item.quantity
                else:
                    order_item.total_price = 0  # Vagy más logika, ha a product nem található

        context = {
            'orders_by_transaction': orders_by_transaction,
            
            'cartItems': cart_items_count,
            'cart_items': cart_items,  # Az aktuális kosár tételei a kontextusban
            'order': order,
            'products': products,
            'items': cart_items

        }
    else:
        # Csak bejelentkezett felhasználóknak üzenet
        context = {
            'message': 'Csak bejelentkezett felhasználóknak!',
            'cartItems': 0,             
            'cart_items': []  # Üres kosár nem bejelentkezett felhasználóknál
            

        }

    return render(request, 'store/order_list.html', context)


from .models import Product, Review
from .forms import ReviewForm
from django.contrib import messages
from django.db import IntegrityError



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    form = ReviewForm()

     # Kosár adatok lekérdezése a cartData függvényből
    cart_data = cartData(request)  # Kosár adatok lekérdezése
    cartItems = cart_data['cartItems']  # Kosár tételek száma
    items = cart_data['items']  # Kosár tételek
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            existing_review = reviews.filter(user=request.user).first()
            if existing_review:
                messages.warning(request, "Már írtál véleményt erről a termékről.")
            else:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.user = request.user
                    review.product = product
                    review.save()
                    messages.success(request, "Köszönjük az értékelésed!")
                else:
                    messages.error(request, "Kérlek, ellenőrizd a mezőket.")

        else:
            messages.error(request, "Bejelentkezés szükséges az értékeléshez.")

    return render(request, 'store/product_detail.html', {
        'product': product,
        'items': items,
        'cartItems': cartItems,
        'reviews': reviews,
        'form': form,
        'show_cart': request.user.is_authenticated,
        'messages': messages.get_messages(request),
    })



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

from django.core.paginator import Paginator

from django.core.paginator import Paginator

def store(request):
    cart_data = cartData(request)  # Kosár adatok lekérdezése
    cartItems = cart_data['cartItems']
    items = cart_data['items']

    sort_by = request.GET.get('sort_by', 'name')  # Alapértelmezett rendezés név szerint
    order = request.GET.get('order', 'asc')  # Alapértelmezett sorrend növekvő
    filter_categories = request.GET.getlist('filter_category', [])  # Több kategória támogatása

    products = Product.objects.all()

    if filter_categories:
        products = products.filter(category__in=filter_categories)

    if sort_by and order:
        if order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')

    paginator = Paginator(products, 6)  # 6 termék oldalanként
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products': products_page,
        'cartItems': cartItems,
        'items': items,
        'selected_categories': filter_categories,
        'sort_by': sort_by,
        'order': order,
    }
    return render(request, 'store/store.html', context)

def reset_filters(request):
    return redirect('store')

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

def index(request):
    cart_data = cartData(request)  # Kosár adatok lekérdezése a cartData függvényből
    cartItems = cart_data['cartItems']
    items = cart_data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'items': items}
    return render(request, 'store/index.html', context)



