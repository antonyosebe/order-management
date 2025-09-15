from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        return ' > '.join([c.name for c in self.get_ancestors(include_self=True)])


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    categories = models.ManyToManyField(
        Category,
        related_name='products',
        help_text="A product can belong to multiple categories"
    )

    sku = models.CharField(max_length=50, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_digital = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 or self.is_digital

    @property
    def primary_category(self):
        return self.categories.first()
