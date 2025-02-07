from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

# Create your views here.

def cart_summary(request):
    # Get the cart
    cart = Cart(request)
    # Get the products
    cart_products = cart.get_prods
    return render(request, 'cart_summary.html', {'cart_products': cart_products})

def cart_add(request):
    # Get the cart
    cart = Cart(request)
    # Test for POST request
    if request.POST.get('action') == 'post':
        # Get Stuff
        product_id = int(request.POST.get('product_id'))
        # Lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        # save to a session
        cart.add(product=product)

        # Get Cart Quantity
        cart_quantity = cart.__len__()

        # Return response
        # response = JsonResponse({'Product Name': product.name})
        response = JsonResponse({'qty': cart_quantity})
        return response

def cart_delete(request):
    pass

def cart_update(request):
    pass