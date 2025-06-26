from django.http import HttpResponse
import json
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import *
from random import sample
import uuid
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib.auth.hashers import make_password

from django.contrib.auth.hashers import check_password

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from datetime import timedelta,datetime
import qrcode
import os
from decimal import Decimal

def checkout_payment(request):
    order_id = request.session.get('orderid')
    order = get_object_or_404(Order, orderid=order_id)
    
    delivery_date = order.created_at + timedelta(days=3)
    return render(request, 'checkout-payment.html', {'order': order,'delivery_date':delivery_date})

import qrcode
import os
from django.conf import settings

def process_payment(request):
    if request.method == 'POST':
        payment_mode = request.POST.get('payment_mode')
        order_id = request.session.get('orderid')

        if not order_id:
            return redirect('home')

        order = Order.objects.get(orderid=order_id)

        if payment_mode == 'COD':
            order.payment_status = 'COD'
            order.status = 'Confirmed'
            order.save()
            del request.session['orderid']
            return redirect(f'/orders/?orderid={order_id}')

        elif payment_mode == 'Online':
            upi_id = 'parthgharat0001@oksbi'
            name = 'Parth Gharat'
            amount = order.total
            txn_note = f"Order {order.orderid}"
            txn_id = order.orderid

            upi_link = f"upi://pay?pa={upi_id}&pn={name.replace(' ', '%20')}&am={amount}&cu=INR&tn={txn_note.replace(' ', '%20')}&tr={txn_id}"

            order.payment_status = 'Unverified'
            order.status = 'Confirmed'
            order.save()

            # QR generation path
            qr_filename = f'qr_{order_id}.png'
            qr_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', qr_filename)
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)

            # Generate QR code
            qr = qrcode.make(upi_link)
            qr.save(qr_path)

            qr_url = f"{settings.MEDIA_URL}qrcodes/{qr_filename}"

            return render(request, 'upi_payment.html', {
                'upi_link': upi_link,
                'order_id': order_id,
                'amount': amount,
                'qr_url': qr_url
            })

    return redirect('checkout_payment')




def contact(request):
    return render(request,'contact.html')




def order(request):
    custid = request.session.get('customer_id')

    if not custid:
        # If no customer ID in session, redirect to login page or home
        # You might want to pass a message to the user here
        # For example, using Django's messages framework
        # messages.info(request, "Please log in to view your order history.")
        return redirect('login_register') # Or whichever URL handles login/registration

    try:
        # Get the Customer instance using the custid from session
        customer = Customer.objects.get(custid=custid)
    except Customer.DoesNotExist:
        return redirect('login_register') # Redirect to login

    # Fetch all orders related to this customer, ordered by creation date (newest first)
    # Using .prefetch_related('items__product__images') to optimize database queries
    # for rendering product images in the order items.
    all_customer_orders = Order.objects.filter(custid=customer).order_by('-created_at').prefetch_related('items__product__images')

    # Prepare data for the template
    orders_data = []
    for order_obj in all_customer_orders:
        estimated_delivery_date = order_obj.created_at + timedelta(days=3)
        orders_data.append({
            'order_obj': order_obj,
            'estimated_delivery_date': estimated_delivery_date
        })

    context = {
        'orders_data': orders_data,
        'current_year': datetime.now().year, # For footer if needed
    }

    return render(request, 'orderhistory.html', context)

def orders(request):
    orderid = request.GET.get('orderid')
    order = get_object_or_404(Order, orderid=orderid)
    delivery_date = order.created_at + timedelta(days=3)


    return render(request,'orders.html',{'order':order,'delivery_date':delivery_date})

def feedback_form(request):
    custid = request.GET.get('custid')
    orderid = request.GET.get('orderid')
    productid = request.GET.get('productid')

    if not (custid and orderid and productid):
        return render(request, 'feedback_error.html', {'error': 'Missing required parameters.'})

    customer = get_object_or_404(Customer, pk=custid)
    order = get_object_or_404(Order, pk=orderid)
    product = get_object_or_404(Product, pk=productid)
    primary_image = product.images.order_by('imageid').first()

    if request.method == 'POST':
        message = request.POST.get('message')
        rating = int(request.POST.get('rating'))

        Feedback.objects.create(
            custid=customer,
            order=order,
            product=product,
            message=message,
            rating=rating
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('/')

    return render(request, 'feedback_form.html', {
        'customer': customer,
        'order': order,
        'product': product,
         'primary_image': primary_image,
    })


def login_register(request):
    context = {'login_page': 'show', 'send_otp': 'show'}  # default
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "login":
            email = request.POST['email']
            password = request.POST['password']

            try:
                customer = Customer.objects.get(email=email)
                if check_password(password, customer.password):
                    request.session['customer_id'] = customer.custid
                    messages.success(request, "Login successful!")
                    return redirect(next_url)
                else:
                    messages.error(request, "Invalid credentials")
            except Customer.DoesNotExist:
                messages.error(request, "Invalid credentials")

        elif action == "register":
            email = request.POST['email']
            otp = random.randint(100000, 999999)
            request.session['register_email'] = email
            request.session['otp'] = str(otp)
            request.session['next_url'] = next_url
            send_mail(
                'Your OTP for Registration on Taracelestial',
                f"Hello!\n\nTo complete your registration, please use the One-Time Password (OTP) below:\n\n🔐 OTP: {otp}\n\nThis code is valid for a short time. Do not share it with anyone.\n\nThank you for registering with us!",
                'taracelestial09@gmail.com',
                [email],
                fail_silently=False,
            )

            context['login_page'] = 'notshow'
            context['send_otp'] = 'notshow'

        elif action == "confirm_otp":
            otp_input = request.POST['otp']
            password = request.POST['password']
            hashed_password = make_password(password)
            email = request.session.get('register_email')
            next_url = request.session.get('next_url') or '/'
            if otp_input == request.session.get('otp'):
                if not Customer.objects.filter(email=email).exists():
                    customer = Customer.objects.create(email=email, password=hashed_password)
                    request.session['customer_id'] = customer.custid
                    messages.success(request, "Registration successful!")
                    return redirect(next_url)
                else:
                    messages.error(request, "Email already registered")
            else:
                messages.error(request, "Invalid OTP")

            context['login_page'] = 'notshow'
            context['send_otp'] = 'notshow'

    return render(request, 'login.html', context)

def forgot_password(request):
    step = 'email'
    next_url = request.GET.get('next') or request.POST.get('next') or '/'

    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST['email']
            if Customer.objects.filter(email=email).exists():
                otp = random.randint(100000, 999999)
                request.session['reset_email'] = email
                request.session['reset_otp'] = str(otp)
                request.session['next_url'] = next_url

                send_mail(
                    "Reset Your Password - OTP",
                    f"Hello!\n\nTo reset your password, please use the OTP below:\n\n🔐 OTP: {otp}\n\nDo not share this with anyone.\n\nThanks,\nTaraCelestial Team",
                    'taracelestial09@gmail.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "OTP sent to your email.")
                step = 'otp'
            else:
                messages.error(request, "No account found with that email.")

        elif 'otp' in request.POST:
            entered_otp = request.POST['otp']
            password = request.POST['password']
            confirm = request.POST['confirm_password']
            email = request.session.get('reset_email')
            next_url = request.session.get('next_url') or '/'

            if entered_otp == request.session.get('reset_otp'):
                if password == confirm:
                    try:
                        customer = Customer.objects.get(email=email)
                        customer.password = make_password(password)
                        customer.save()

                        # ✅ Set session
                        request.session['customer_id'] = customer.custid
                        messages.success(request, "Password reset successful and logged in.")
                        return redirect(next_url)
                    except Customer.DoesNotExist:
                        messages.error(request, "Something went wrong. Try again.")
                else:
                    messages.error(request, "Passwords do not match.")
                    step = 'otp'
            else:
                messages.error(request, "Invalid OTP.")
                step = 'otp'

    return render(request, 'forgot_password.html', {'step': step, 'next_url': next_url})

def resend_otp(request):
    email = request.session.get('otp_email')
    if email:
        otp = random.randint(100000, 999999)
        request.session['otp'] = str(otp)
        send_mail(
            'Your New OTP',
            f"Hello!\n\nTo reset your password, please use the OTP below:\n\n🔐 OTP: {otp}\n\nDo not share this with anyone.\n\nThank you.",
            'taracelestial09.com',
            [email],
            fail_silently=False,
        )
        messages.success(request, "New OTP sent")
    return redirect('login_register')


def logout_view(request):
    logout(request)
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


def google_login(request):
    return redirect('login_register')


def google_callback(request):
    return redirect('/')



def home(request):
    cart_items = []
    total_items = 0
    total_price = 0
    custid = request.session.get('customer_id')
    if custid:
        # Logged-in customer
        cart_items = Cart.objects.filter(custid=custid)
    else:
        # Guest using session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key)

    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render(request, 'index.html',{'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price})

def checkout(request):
    if not request.session.get('customer_id'):
        return redirect('/login?next=/checkout')
    return render(request, 'checkout.html')


def checkout(request):
    customer_data = None
    cart_items = []
    total = 0
    if not request.session.get('customer_id'):
        return redirect('/login?next=/checkout')
    custid = request.session.get('customer_id')
    session_key = request.session.session_key
    if not session_key:
        session_key = request.session.save() or request.session.session_key

    if custid:
        customer_data = Customer.objects.filter(custid=custid).first()
        cart_items = Cart.objects.filter(custid=customer_data)

        # If no cart items for this customer, fallback to session cart
        if not cart_items.exists():
            cart_items = Cart.objects.filter(session_key=session_key)
    else:
        # Guest user
        cart_items = Cart.objects.filter(session_key=session_key)

    # Calculate total
    for item in cart_items:
        total += item.quantity * item.product.price

    return render(request, 'checkout.html', {
        'customer': customer_data,
        'cart_items': cart_items,
        'total': total,
    })

def product(request):
    # Fetch all products, prefetch their images for efficiency
    all_products = Product.objects.all().prefetch_related('images')

    # Prepare products data for JSON serialization
    products_data_for_json = []
    for product in all_products:
        # Get the URL of the first image, or a placeholder if no images
        image_url = ''
        if product.images.first() and product.images.first().image:
            image_url = product.images.first().image.url

        products_data_for_json.append({
            'product_id': product.product_id,
            'name': product.name,
            'brand': product.brand,
            'desc': product.desc,
            'price': float(product.price),        # Convert Decimal to float
            'fake_price': float(product.fake_price), # Convert Decimal to float
            'stock': product.stock,
            'image_url': image_url,
        })

    # Dump the Python list of dictionaries to a JSON string
    products_json = json.dumps(products_data_for_json)

    context = {
        'products_json': products_json, # Pass this JSON string to the template
        # You can also pass the queryset if you need it for server-side logic/initial render without JS
        'products': all_products # Keeping this for initial rendering if JS fails or for debugging
    }
    return render(request, 'allproducts.html', context)



def place_order(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        session_key = request.session.session_key or request.session.save()

        cart_items = None
        customer = None

        if customer_id:
            customer = Customer.objects.get(pk=customer_id)
            # Fetch and update contact info (fallback to blank if missing)
            customer.first = request.POST.get("first")
            customer.last = request.POST.get("last")
            customer.address = request.POST.get("address")
            customer.state = request.POST.get("state")
            customer.city = request.POST.get("city")
            customer.zipcode = request.POST.get("zipcode")
            customer.phone = request.POST.get("phone")

            

            customer.save()

            # Get cart for customer
            cart_items = Cart.objects.filter(custid=customer)
            if not cart_items.exists():
                cart_items = Cart.objects.filter(session_key=session_key)
        else:
            cart_items = Cart.objects.filter(session_key=session_key)

        if not cart_items.exists():
            return redirect('cart')  # Or show a message like: cart is empty

        total = sum(item.product.price * item.quantity for item in cart_items)

        # Shipping address (may be same as contact)
        daddress = request.POST.get("daddress")
        dcity = request.POST.get("dcity")
        dstate = request.POST.get("dstate")
        dzipcode = request.POST.get("dzipcode")

        if not all([daddress, dcity, dstate, dzipcode]):
            return redirect('checkout')  # Or show an error

        # Create order
        order = Order.objects.create(
            custid=customer,
            total=Decimal(total),
            daddress=daddress,
            dcity=dcity,
            dstate=dstate,
            dzipcode=dzipcode,
            status='Payment Pending',
            payment_status='Not done',
        )

        # Add items to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        request.session['orderid']=order.orderid
        # Clear the cart
        cart_items.delete()

        return redirect('checkout_payment')  # Or payment page

    return redirect('checkout')



def get_cart_items(request):
    session_key = request.session.session_key or request.session.create()
    custid = request.session.get('customer_id')

    if custid:
        cart_items = Cart.objects.filter(custid_id=custid)
    else:
        cart_items = Cart.objects.filter(session_key=session_key)

    grand_total = sum(item.product.price * item.quantity for item in cart_items)

    return cart_items, grand_total


def cart(request):
    cart_items, grand_total = get_cart_items(request)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })

def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    session_key = request.session.session_key or request.session.create()
    custid = request.session.get('customer_id')

    if custid:
        cart_item = Cart.objects.filter(custid_id=custid, product_id=product_id).first()
    else:
        cart_item = Cart.objects.filter(session_key=session_key, product_id=product_id).first()

    if cart_item:
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request):
    product_id = request.POST.get('product_id')

    session_key = request.session.session_key
    custid = request.session.get('customer_id')

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if custid:
        cart_item = Cart.objects.filter(custid=custid, product_id=product_id).first()
    else:
        cart_item = Cart.objects.filter(session_key=session_key, product_id=product_id).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url', '/')

        # Get session key or create it
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Check if customer is logged in
        custid = request.session.get('customer_id')

        if custid:
            # Logged in customer
            customer_instance = Customer.objects.get(pk=custid)
            cart_item, created = Cart.objects.get_or_create(
                custid=customer_instance,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            # Guest user
            cart_item, created = Cart.objects.get_or_create(
                session_key=session_key,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        return redirect(redirect_url)
    


def product_details(request):
    product_id = request.GET.get('productid')
    product = get_object_or_404(Product, product_id=product_id)

    # Feedback & Ratings
    feedback_qs = Feedback.objects.filter(product=product).select_related('custid').order_by('-id')
    for fb in feedback_qs:
        fb.star_list = ["1"] * fb.rating

    rating_counts_raw = feedback_qs.values('rating').annotate(count=Count('rating'))
    rating_counts = {i: 0 for i in range(1, 6)}
    for item in rating_counts_raw:
        rating_counts[item['rating']] = item['count']

    total_reviews = sum(rating_counts.values())
    avg_rating = round(feedback_qs.aggregate(avg=Avg('rating'))['avg'] or 0, 1)
    rating_counts["ars"] = ["0"] * int(avg_rating)

    rating_percentages = {
        i: int((rating_counts[i] / total_reviews) * 100) if total_reviews else 0
        for i in range(1, 6)
    }

    product_images = product.images.all()

    # Related Products
    product_ids = list(Product.objects.exclude(product_id=product_id).values_list('product_id', flat=True))
    selected_ids = sample(product_ids, min(8, len(product_ids)))
    related_products = Product.objects.filter(product_id__in=selected_ids)
    for p in related_products:
        p.main_image = p.images.order_by('imageid').first()

    # Cart Handling
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = []
    total_items = 0
    total_price = 0
    custid = request.session.get('customer_id')
    if custid:
        # Logged-in customer
        cart_items = Cart.objects.filter(custid=custid)
    else:
        # Guest using session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = Cart.objects.filter(session_key=session_key)

    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render(request, 'product.html', {
        'product': product,
        'product_images': product_images,
        'feedback_list': feedback_qs,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
        'avg_rating_percent': int((avg_rating / 5) * 100),
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    })



#owner


def admin_login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            owner = Owner.objects.get(username=username)
            if check_password(password, owner.password):
                request.session['owner_id'] = owner.id
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid username or password")
        except Owner.DoesNotExist:
            messages.error(request, "Invalid username or password")

    return render(request, 'owner/admin_login.html')

def admin_dashboard(request):
    if not request.session.get('owner_id'):
        return redirect('admin_login')  # redirect to login if not logged in
    return render(request, 'owner/admin_dashboard.html')




def product_management_page(request):
    if not request.session.get('owner_id'):
        return redirect('admin_login')
    
    products = Product.objects.all()
    return render(request, 'owner/product_management.html', {'products': products})



def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        brand = request.POST.get('brand')
        composition = request.POST.get('composition')
        care = request.POST.get('care')

        price = Decimal(request.POST.get('price'))
        fake_price = Decimal(request.POST.get('fake_price'))
        stock = int(request.POST.get('stock'))


        product = Product.objects.create(
            name=name,
            desc=desc,
            price=price,
            fake_price=fake_price,
            stock=stock,
            brand=brand,
            composition=composition,
            care=care
        )

        images = request.FILES.getlist('images')
        for image in images:
            ext = os.path.splitext(image.name)[1]  # get extension like '.jpg'
            unique_name = f"{uuid.uuid4().hex}{ext}"
            image.name = unique_name  # override the name

            ProductImage.objects.create(product=product, image=image)
        
        messages.error(request, "Product Added!!")

        return redirect('add_product')  # Change this to your redirect URL name

    return render(request, 'owner/add_product.html')






def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.desc = request.POST['description']
        product.price = request.POST['price']
        product.fake_price = request.POST['fake_price']
        product.stock = request.POST['stock']
        product.save()
        messages.error(request, f"Product {product.name} Update!!")
        return redirect('product_management_page')

    return render(request, 'owner/edit_product.html', {'product': product})
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.delete()
    messages.error(request, f"Product {product_id} Deleted!!")
    return redirect('product_management_page')



def category_management_page(request):
    return render(request, 'owner/category_management.html')

def order_management_page(request):
    # Fetch all orders, prefetch related Customer, OrderItem, and Product for efficiency
    orders_queryset = Order.objects.select_related('custid').prefetch_related('items__product').all().order_by('-created_at')

    # Prepare data for JSON serialization
    orders_data_for_json = []
    for order in orders_queryset:
        items_data = []
        for item in order.items.all():
            items_data.append({
                'product_id': item.product.product_id, # Include product ID
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': float(item.price), # Convert Decimal to float
            })

        orders_data_for_json.append({
            'orderid': order.orderid,
            'customer': {
                'custid': order.custid.custid,
                'name': f"{order.custid.first} {order.custid.last}", # Combine first and last name
                'email': order.custid.email,
                'phone': order.custid.phone,
                # For address, combine all components if needed, or pass separately
                'address': order.daddress, # Use delivery address from Order model
                'city': order.dcity,
                'state': order.dstate,
                'zipcode': order.dzipcode,
            },
            'total': float(order.total), # Convert Decimal to float
            'delivery_address': f"{order.daddress}, {order.dcity}, {order.dstate}, {order.dzipcode}", # Full delivery address
            'status': order.status,
            'payment_status': order.payment_status,
            'created_at': order.created_at.isoformat(), # Convert datetime to ISO format string
            'items': items_data,
        })

    # Dump the Python list of dictionaries to a JSON string
    orders_json = json.dumps(orders_data_for_json)

    context = {
        'orders_json': orders_json, # This is what you'll pass to the template
        # You can still pass the original queryset if you need it for direct Django template looping,
        # but the modal will use orders_json.
        'orders': orders_queryset, # Keep this for the main list display if you want
    }
    return render(request, 'owner/order_management.html', context)



def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Shipped', 'Delivered']:
            order.status = new_status
            order.save()
    return redirect('order_management_page')

def update_order_payment_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, orderid=order_id)
        payment_status = request.POST.get('payment_status')
        order.payment_status = payment_status
        order.save()
        return redirect('order_management_page')

def customer_list_page(request):
    return render(request, 'owner/customer_list.html')