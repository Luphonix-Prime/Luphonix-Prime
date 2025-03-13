from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from .models import NavbarLink, Product, Cart, Order, Category
from .forms import CartForm, ProductForm, EmailChangeForm, EditProfileForm, ChangePasswordForm, CategoryForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import logout,update_session_auth_hash
from django import forms
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import connection  # To reset the database sequence

from django.views.decorators.csrf import csrf_exempt
from faker import Faker
fake = Faker()

from datetime import datetime, timedelta
from django.db.models import Sum, Count
class CustomLoginView(LoginView):
    template_name = 'store/login.html'  # Use your custom login template

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return '/dashboard'  # Redirect admins and staff to the dashboard
        return '/products'  # Redirect normal users to the product list




def add_to_cart(request, product_slug):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to log in to add items to your cart.")
        return redirect('login')  

    product = get_object_or_404(Product, slug=product_slug)
    quantity = request.POST.get('quantity', 1)

    try:
        quantity = max(1, int(quantity))  # Ensure quantity is at least 1
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect('cart')

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, defaults={'quantity': quantity})

    if not created:
        cart_item.quantity += quantity  # Increase quantity if already in cart
        cart_item.save(update_fields=['quantity'])

    messages.success(request, f"{quantity}x {product.name} added to cart!")  
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})


def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:  # If cart is empty, prevent checkout
        return redirect('cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        order = Order.objects.create(user=request.user, total_price=total_price)

        # Move cart items to order (optional - depends on your needs)
        for item in cart_items:
            item.delete()  # Clear the cart after checkout

        return redirect('order_success')

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

def order_success(request):
    return render(request, 'store/order_success.html')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    confirm_email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "confirm_email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError("Emails do not match")

        return cleaned_data

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'store/profile.html', {'user': request.user})

@login_required
@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save to DB yet
            product.slug = slugify(product.name)  # Auto-generate slug
            product.save()  # Save with the new slug
            return redirect('product_list')  # Redirect to product list after adding
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})
 
@login_required
def change_email(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after email update
    else:
        form = EmailChangeForm(instance=request.user)
    
    return render(request, 'store/change_email.html', {'form': form})


def update_cart(request, product_slug):
    cart_item = get_object_or_404(Cart, slug=product_slug, user=request.user)

    if request.method == "POST":
        new_quantity = request.POST.get("quantity")
        if new_quantity and int(new_quantity) > 0:
            cart_item.quantity = int(new_quantity)
            cart_item.save()
        else:
            cart_item.delete()  # If the quantity is 0, remove the item from the cart

    return redirect('cart')  # Redirect back to cart page

def remove_from_cart(request, product_slug):
    cart_item = get_object_or_404(Cart, slug=product_slug, user=request.user)
    cart_item.delete()
    return redirect('cart')  # Redirect back to cart page


@login_required
def profile(request):
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                if request.user.check_password(password_form.cleaned_data['current_password']):
                    request.user.set_password(password_form.cleaned_data['new_password'])
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # Keep user logged in
                    messages.success(request, "Password changed successfully!")
                    return redirect('profile')
                else:
                    messages.error(request, "Current password is incorrect.")

    return render(request, 'store/profile.html', {'password_form': password_form})


@login_required
def edit_profile(request):
    form = EditProfileForm(instance=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    return render(request, 'store/edit_profile.html', {'form': form})




def edit_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    categories = Category.objects.all()

    if request.method == "POST":
        print("📨 POST request received!")  # Debugging
        print("📝 Form Data:", request.POST)  # Debugging: Print form data
        print("📂 Files Data:", request.FILES)  # Debugging: Print uploaded files

        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            print("✅ Form is valid!")  # Debugging
            form.save()
            print("✅ Product updated successfully!")  # Debugging
            return redirect('product_list')  # Redirect after saving
        else:
            print("❌ Form Errors:", form.errors)  # Debugging

    else:
        form = ProductForm(instance=product)

    return render(request, 'store/edit_product.html', {'form': form, 'product': product, 'categories': categories})

@login_required
def delete_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    product.delete()
    return redirect('product_list') 

def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.prefetch_related('products').all()  # Use 'products' instead of 'product_set'
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})






# List Categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/categories.html', {'categories': categories})

# Add Category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')  # Make sure this URL name exists
    else:
        form = CategoryForm()
    
    return render(request, 'store/add_category.html', {'form': form})


# Edit Category
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'store/edit_category.html', {'form': form, 'category': category})


# Delete Category
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('categories')
    return render(request, 'store/delete_category.html', {'category': category})

# Check if user is admin
def is_admin(user):
    return user.is_staff

# Admin Dashboard

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    products = Product.objects.all()  # Fetch products from DB
    categories = Category.objects.all() 

    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    users = User.objects.all()
# Get selected report type
    report_type = request.GET.get('report_type', 'monthly')

    # Define report title
    report_title = "📅 Monthly Sales Report" if report_type == "monthly" else "📆 Yearly Sales Report"

     # Get the current date
    current_date = now()
    # Get sales data based on selection
    if report_type == "monthly":
        start_date = current_date.replace(day=1)  # First day of the current month
        end_date = current_date  # Today's date (to ensure proper filtering)
        total_sales = Order.objects.filter(created_at__year=current_date.year, created_at__month=current_date.month).aggregate(total=Sum('total_price'))['total'] or 0
        total_orders = Order.objects.filter(created_at__year=current_date.year, created_at__month=current_date.month).count()
    else:  # Yearly Report
        start_date = current_date.replace(month=1, day=1)  # First day of the year
        total_sales = Order.objects.filter(created_at__year=current_date.year).aggregate(total=Sum('total_price'))['total'] or 0
        total_orders = Order.objects.filter(created_at__year=current_date.year).count()
        
    context = {
        'users': users,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        "report_type": report_type,
        "report_title": report_title,
        "total_sales": total_sales,
        "total_orders": total_orders,
        'products': products,
        'categories': categories
    }
    return render(request, 'store/dashboard.html', context)

# Toggle Staff Status
@login_required
@user_passes_test(is_admin)
def toggle_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.is_staff = not user.is_staff
        user.save()
    return redirect('dashboard')

# Delete User
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
    return redirect('dashboard')

def clear_report(request):
    if request.method == "POST":
        Order.objects.all().delete()  # ⚠️ Deletes all orders!
        messages.success(request, "All orders have been cleared.")
        return redirect('dashboard')
    
def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    
    return render(request, 'store/search_results.html', {'query': query, 'products': products})

def report_page(request):
    orders = Order.objects.all()  # Fetch all orders
    total_revenue = sum(order.total_price for order in orders)  # Calculate revenue
    total_orders = orders.count()  # Count total orders

    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
    }
    return render(request, 'store/report.html', context)


def clear_report(request):
    if request.method == "POST":
        Order.objects.all().delete()  # Delete all orders
        messages.success(request, "All reports cleared successfully.")
        return redirect('reset_order_sequence')  # Redirect to reset page

def reset_order_sequence(request):
    if request.method == "POST":
        choice = request.POST.get("sequence_choice")

        with connection.cursor() as cursor:
            if choice == "reset_to_1":
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_order'")  # Reset ID to 1
            elif choice == "continue_from_last":
                last_order = Order.objects.last()  # Get last order (if any)
                new_start = (last_order.id + 1) if last_order else 1
                cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name='store_order'", [new_start - 1])  

        messages.success(request, "Order sequence updated successfully.")
        return redirect('report_page')  # Redirect back to report page

    return render(request, "store/reset_order_sequence.html")

def navbar_data(request):
    categories = Category.objects.all()
    navbar_links = NavbarLink.objects.all()
    return {'categories': categories, 'navbar_links': navbar_links}

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {'category': category, 'products': products})

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'store/product_detail.html', {'product': product})

fake = Faker()

@csrf_exempt  # If CSRF is causing issues
def get_fake_products(request):
    num = request.GET.get('num', 5)  # Get 'num' from request
    try:
        num = int(num)  # Convert to integer
        num = max(1, min(num, 20))  # Limit between 1-20
    except ValueError:
        return JsonResponse({"error": "Invalid number"}, status=400)

    fake_products = []
    for _ in range(num):  # Generate the requested number of fake products
        fake_products.append({
            "name": fake.word().capitalize() + " Product",
            "price": round(fake.random_number(digits=2) + 0.99, 2),
            "description": fake.sentence(),
        })

    return JsonResponse(fake_products, safe=False)

def fake_products_page(request):
    return render(request, "store/fake_products.html")