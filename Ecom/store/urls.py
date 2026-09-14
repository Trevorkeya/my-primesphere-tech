from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Authentication URLs
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name ='register'),

    # User Account URLs
    path('update_password/', views.update_password, name='update_password'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),

    # Product URLs
    path('product/<int:pk>/', views.product, name='product'),

    # Category URLs
    path('category/<str:foo>/', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),

    # Search URL
    path('search/', views.search, name ='search'),

    # Vendor URLs
    path('apply_vendor/', views.apply_vendor, name='apply_vendor'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/add-product/', views.add_product, name='add_product'),

    # Vendor Order Management URLs
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('vendor/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('vendor/delete-product/<int:pk>/', views.delete_product, name='delete_product'),

]

