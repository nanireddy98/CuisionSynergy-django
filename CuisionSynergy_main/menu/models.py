from django.db import models
from vendor.models import Vendor


class Category(models.Model):
    """Model representing a category of food items"""
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)   # Each category is associated with a vendor; deleting a vendor will delete its categories
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50,unique=True)   # Unique slug for URL identification
    description = models.TextField(max_length=250,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def clean(self):
        """Capitalize the category name before saving"""
        self.category_name = self.category_name.capitalize()

    def __str__(self):
        """String representation of the category"""
        return self.category_name


class FoodItem(models.Model):
    """Model representing a food item"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='fooditems')
    food_title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    image = models.ImageField(upload_to='foodimages')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the food item"""
        return self.food_title
