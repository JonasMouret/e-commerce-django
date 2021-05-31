from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from PIL import Image, ImageOps
from django_countries.fields import CountryField

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

class Category(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

class Item(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='items-images/', blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField(max_length=200)
    slug = models.SlugField()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})

    def get_add_to_card_url(self):
        return reverse('core:add-to-card', kwargs={'slug': self.slug})

    def get_remove_from_card_url(self):
        return reverse('core:remove-from-card', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.image :
            super(Item, self).save()
            img = Image.open(self.image.path)
            if img.format != 'JPEG' or img.format != 'JPG':
                img = img.convert('RGB')
            img.thumbnail(size=(400,400))
            img.save(self.image.path, format="JPEG", optimize=True, quality=70)

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username