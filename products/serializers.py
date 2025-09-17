from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories, including nested children and product counts."""
    children = serializers.SerializerMethodField()
    full_path = serializers.ReadOnlyField()
    level = serializers.ReadOnlyField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "parent",
            "children", "level", "full_path", "product_count",
            "is_active", "created_at"
        ]
        read_only_fields = ["created_at"]

    def get_children(self, obj):
        """Return direct child categories, if any."""
        children = obj.get_children()
        return CategorySerializer(children, many=True).data if children.exists() else []

    def get_product_count(self, obj):
        """Count all products under this category, including descendants."""
        related_categories = obj.get_descendants(include_self=True)
        return Product.objects.filter(categories__in=related_categories).distinct().count()


class CategoryAveragePriceSerializer(serializers.Serializer):
    """Serializer used for reporting average price of products within a category."""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_count = serializers.IntegerField()
    include_subcategories = serializers.BooleanField(default=True)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products, with category details and stock info."""
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    primary_category = CategorySerializer(read_only=True)
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description",
            "price", "cost_price", "sku", "stock_quantity",
            "is_digital", "is_active", "is_featured",
            "categories", "category_ids", "primary_category",
            "is_in_stock", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        category_ids = validated_data.pop("category_ids", [])
        product = Product.objects.create(**validated_data)

        if category_ids:
            product.categories.set(Category.objects.filter(id__in=category_ids))

        return product

    def update(self, instance, validated_data):
        category_ids = validated_data.pop("category_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))

        return instance


class ProductUploadSerializer(serializers.Serializer):
    """Serializer for bulk product upload."""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sku = serializers.CharField(max_length=50)
    stock_quantity = serializers.IntegerField(default=0)
    is_digital = serializers.BooleanField(default=False)
    category_names = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of category names; new ones will be created if missing."
    )

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value
