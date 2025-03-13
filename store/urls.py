from django.urls import path
from . import views
from .views import (
    CustomLoginView, category_detail, clear_report, delete_user, fake_products_page, get_fake_products,  product_list, product_detail, add_to_cart, 
    cart_view, checkout, order_success, remove_from_cart, reset_order_sequence, search_results, toggle_staff, update_cart,
    category_list, profile_view, add_product, change_email, report_page, clear_report, edit_product, edit_profile, dashboard, delete_product
)
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)

urlpatterns = [
    path('', dashboard, name='index'),  # 👈 Landing page is now the dashboard
     path('dashboard/', dashboard, name='dashboard'),
     path('dashboard/clear-report/', clear_report, name='clear_report'),
    path('products/', product_list, name='product_list'),  # 👈 Using imported product_list
    # path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<slug:product_slug>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/', order_success, name='order_success'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('add-product/', add_product, name='add_product'),

    
    path('change-email/', change_email, name='change_email'),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Password Change
    path('password-change/', PasswordChangeView.as_view(template_name='store/password_change.html'), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='store/password_change_done.html'), name='password_change_done'),

    # Password Reset
    path('password-reset/', PasswordResetView.as_view(template_name='store/password_reset.html'), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='store/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='store/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='store/password_reset_complete.html'), name='password_reset_complete'),
    
    path('product/edit/<slug:product_slug>/', edit_product, name='edit_product'),
    path('product/delete/<slug:product_slug>/', delete_product, name='delete_product'),
    
    path('categories/', category_list, name='categories'),
    path('category/<slug:category_slug>/', category_detail, name='category_detail'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('add-category/', views.add_category, name='add_category'),  # These are not in the imported list
    path('edit-category/<slug:category_slug>/', views.edit_category, name='edit_category'),
    path('delete-category/<slug:category_slug>/', views.delete_category, name='delete_category'),
    
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', update_cart, name='update_cart'),
    path('toggle-staff/<int:user_id>/', toggle_staff, name='toggle_staff'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('search/', search_results, name='search_results'),
    
    path('report/', report_page, name='report_page'),
    path('clear_report/', clear_report, name='clear_report'),
    path('reset_order_sequence/', reset_order_sequence, name='reset_order_sequence'),
    
     path("get_fake_products/", get_fake_products, name="fake-products"),
    path("fake-products-page/", fake_products_page, name="fake-products-page"),
]
