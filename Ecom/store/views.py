from django.shortcuts import render, redirect
from .models import Product, Category, Profile, Vendor
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.contrib.auth.decorators import login_required

from payment.forms import ShippingForm
from payment.models import ShippingAddress, OrderItem
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart

# Create your views here.

@login_required
def add_product(request):

    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect("apply_vendor")

    if not vendor.is_approved:
        return render(request, "vendor/pending_approval.html")

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = Category.objects.get(id=category_id)

        Product.objects.create(
            vendor=vendor,
            name=name,
            price=price,
            description=description,
            category=category,
            image=image
        )

        messages.success(request, "Product created successfully!")
        return redirect("vendor_dashboard")

    categories = Category.objects.all()

    return render(request, "vendor/add_product.html", {"categories": categories})

@login_required
def vendor_dashboard(request):

    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect("apply_vendor")

    if not vendor.is_approved:
        return render(request, "vendor/pending_approval.html")

    products = Product.objects.filter(vendor=vendor)
    orders = OrderItem.objects.filter(product__vendor=vendor)

    total_revenue = 0

    for item in orders:
        total_revenue += item.price * item.quantity

    context = {
        "vendor": vendor,
        "products": products,
        "orders": orders,
        "total_revenue": total_revenue,
    }

    return render(request, "vendor/dashboard.html", context)

@login_required
def apply_vendor(request):
    if request.method == "POST":
        store_name = request.POST.get("store_name")
        description = request.POST.get("description")

        # Only create if the user doesn't already have a vendor profile
        vendor, created = Vendor.objects.get_or_create(
            user=request.user,
            defaults={'store_name': store_name, 'description': description}
        )

        if not created:
            messages.warning(request, "You have already applied to be a vendor.")
            return redirect('home')

        messages.success(request, "Application submitted! Wait for approval.")
        return render(request, "vendor/application_submitted.html")

    return render(request, "vendor/apply_vendor.html")


def search(request):
    # Determine if they filled out the form 
    if request.method == "POST":
        searched = request.POST['searched']
        # Query The Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched)| Q(description__icontains=searched))
        # Test For Null
        if not searched:
            messages.warning(request, "Sorry That Product Does Not Exist. . .Please Try Again!!!")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {'searched':searched})
    else:
        return render(request, "search.html", {})
    

def update_info(request):
    # First make sure this sis a logged in user
    if request.user.is_authenticated:
        # Get current user info
        current_user = Profile.objects.get(user__id=request.user.id)
        # Get current user shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Get current user Info form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Get current user Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save() #original User Form
            shipping_form.save() #Shipping Form
            messages.success(request, 'Your info has been updated successfully.')
            return redirect('home')
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.warning(request, 'You Must be logged In To Access That Page!!!')
        return redirect('home')

def update_password(request):
    # First make sure this is a logged in user
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form?
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid 
            if  form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated, Please Log in Again. . . ")
                login(request, current_user)
                return redirect('update_user')
            else:
                # If the form is not valid, show the errors
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.warning(request, 'You Must be logged In To View That Page!!!')
        return redirect('home')

def update_user(request):
    # First make sure this sis a logged in user
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, 'User information updated successfully.')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.warning(request, 'You Must be logged In To View That Page!!!')
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})
    
def category(request, foo):
    # Replace the hyphen with a space
    foo = foo.replace('-', ' ')
    # Grab the category from the url
    try:
        # Look up the category by name
        category = Category.objects.get(name=foo)
        # Get all the products that belong to the category
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.error(request, 'Category does not exist.')
        return redirect('home')

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            # Shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get the old cart(saved cart) from the Profile Model
            saved_cart = current_user.old_cart
            # Convert the string to a dictionary
            if saved_cart:
                # convert using json.loads
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to the session cart
                cart = Cart(request)
                # Loop through the cart and add the items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, 'You have been logged in!')
            return redirect('home')
        else:
            messages.warning(request, 'Login failed! ! ! Please try again.')
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out. . . thanks for stopping by!')
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.warning(request, "Passwords do not match! ! !")
            return redirect("login")

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken! ! !")
            return redirect("login")

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already registered! ! !")
            return redirect("login")

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()

        login(request, user)
        messages.success(request, "Registration successful. Please fill out Your User info below.")
        return redirect("update_info")

    return render(request, "login.html")