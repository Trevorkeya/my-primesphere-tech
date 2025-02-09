from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django import forms

# Create your views here.

def update_info(request):
    # First make sure this sis a logged in user
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your info has been updated successfully.')
            return redirect('home')
        return render(request, 'update_info.html', {'form': form})
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