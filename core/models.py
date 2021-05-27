from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from PIL import Image, ImageOps

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


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
