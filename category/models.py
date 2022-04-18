from distutils.command.upload import upload
from pydoc import describe
from tokenize import blank_re
from turtle import Turtle
from unicodedata import category
from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    # slug is the url of the category
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    # To Change plural form of category in admin panel
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # This function give us the url of category
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    # String representation of Models Category
    def __str__(self):
        return self.category_name