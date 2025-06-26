from django.contrib import admin

from .models import * # 1. Import your models

# 2. Register your models here.
admin.site.register(Owner)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Feedback)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(OrderItem)

