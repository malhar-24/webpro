from django.db import models


# -------------------- Product --------------------
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    desc = models.TextField()
    composition = models.TextField()
    care = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    fake_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name

# -------------------- Customer --------------------
class Customer(models.Model):
    custid = models.AutoField(primary_key=True)
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode=models.CharField(max_length=15)
    password = models.CharField(max_length=128)  # Store hashed passwords in real projects

    def __str__(self):
        return self.first

# -------------------- Product Image --------------------

class ProductImage(models.Model):
    imageid=models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"Image {self.image} for {self.product.name}"

# -------------------- Cart --------------------
class Cart(models.Model):
    session_key = models.CharField(max_length=100, null=True, blank=True)  # For guests
    custid = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True)  # For logged-in users
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = (('session_key', 'product'), ('custid', 'product'))

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity}"

# -------------------- Order --------------------
class Order(models.Model):
    orderid = models.AutoField(primary_key=True)
    custid = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    daddress = models.TextField()
    dcity = models.CharField(max_length=255)
    dstate = models.CharField(max_length=255)
    dzipcode=models.CharField(max_length=15)
    status = models.CharField(max_length=50)  # e.g., Pending, Shipped, Delivered
    payment_status = models.CharField(max_length=50,null=True, blank=True) #done,cod
    created_at = models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return f"Order {self.orderid}"

# -------------------- Order Item --------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# -------------------- Feedback --------------------
class Feedback(models.Model):
    custid = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.custid.custid}"
class Owner(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # In production, store hashed passwords

    def __str__(self):
        return self.username
