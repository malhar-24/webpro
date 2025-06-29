# Generated by Django 5.2.1 on 2025-06-25 23:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('custid', models.AutoField(primary_key=True, serialize=False)),
                ('first', models.CharField(max_length=255)),
                ('last', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('zipcode', models.CharField(max_length=15)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('brand', models.CharField(max_length=255)),
                ('desc', models.TextField()),
                ('composition', models.TextField()),
                ('care', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fake_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('orderid', models.AutoField(primary_key=True, serialize=False)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('daddress', models.TextField()),
                ('dcity', models.CharField(max_length=255)),
                ('dstate', models.CharField(max_length=255)),
                ('dzipcode', models.CharField(max_length=15)),
                ('status', models.CharField(max_length=50)),
                ('payment_status', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='App.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.product')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('rating', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.customer')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('imageid', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='App.product')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('custid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.product')),
            ],
            options={
                'unique_together': {('custid', 'product'), ('session_key', 'product')},
            },
        ),
    ]
