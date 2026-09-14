from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile, Vendor
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)



class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    actions = ['approve_vendors']

    def approve_vendors(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected vendors have been approved!")

admin.site.register(Vendor, VendorAdmin)

# Mix Profile Info and User Info
class ProfileInline(admin.StackedInline):
    model = Profile
    
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'email', 'first_name', 'last_name']
    inlines = [ProfileInline]

# Unregister the Old Way
admin.site.unregister(User)

# Re-Register the New Way
admin.site.register(User, UserAdmin)

