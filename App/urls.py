from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/',views.product, name='product'),
    path('products/',views.product_details, name='product_details'),
    path('checkout_payment/', views.checkout_payment, name='checkout_payment'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/',views.cart, name='cart'),
    path('place_order/', views.place_order, name='place_order'),
    path('process_payment/',views.process_payment,name='process_payment'),
    path('order/',views.order, name='order'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('orders/',views.orders, name='orders'),
    path('contact/',views.contact, name='contact'),
    path('feedback/', views.feedback_form, name='feedback_form'),

    path('login/', views.login_register, name='login_register'),
    path('logout/', views.logout_view, name='logout_view'),
    path('google-login/', views.google_login, name='google_login'),
    path('google-register/', views.google_login, name='google_register'),  # using same placeholder



    # Admin Pages (custom prefix 'adminpanel/' to avoid conflict)
    path('adminpanel/login/', views.admin_login_page, name='admin_login'),
    path('adminpanel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('adminpanel/products/', views.product_management_page, name='product_management_page'),
    path('adminpanel/orders/', views.order_management_page, name='order_management_page'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('update_order_payment_status/<int:order_id>/', views.update_order_payment_status, name='update_order_payment_status'),

    
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

