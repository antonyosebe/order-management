from django.db.models import Avg, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CategoryAveragePriceSerializer,
    ProductUploadSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD and custom actions for product categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter categories (active only, with optional parent filter)."""
        qs = Category.objects.filter(is_active=True)
        parent_id = self.request.query_params.get("parent")

        if parent_id == "root":
            return qs.filter(parent=None)
        elif parent_id:
            return qs.filter(parent_id=parent_id)
        return qs

    @action(detail=True, methods=["get"])
    def average_price(self, request, slug=None):
        """Return average product price for this category."""
        category = self.get_object()
        include_subs = request.query_params.get("include_subcategories", "true").lower() == "true"
        categories = category.get_descendants(include_self=True) if include_subs else [category]

        products = Product.objects.filter(categories__in=categories, is_active=True).distinct()
        avg_price = products.aggregate(value=Avg("price"))["value"]
        product_count = products.count()

        data = {
            "category_id": category.id,
            "category_name": category.name,
            "average_price": avg_price or 0,
            "product_count": product_count,
            "include_subcategories": include_subs,
        }
        return Response(CategoryAveragePriceSerializer(data).data)

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        """List products belonging to this category """
        category = self.get_object()
        include_subs = request.query_params.get("include_subcategories", "true").lower() == "true"
        categories = category.get_descendants(include_self=True) if include_subs else [category]

        products = Product.objects.filter(categories__in=categories, is_active=True).distinct()
        return Response(ProductSerializer(products, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD and bulk upload for products."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter products by category, search term, or stock status."""
        qs = Product.objects.filter(is_active=True)

        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(categories__id=category_id)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )

        in_stock = self.request.query_params.get("in_stock")
        if in_stock is not None:
            if in_stock.lower() == "true":
                qs = qs.filter(Q(stock_quantity__gt=0) | Q(is_digital=True))
            else:
                qs = qs.filter(stock_quantity=0, is_digital=False)

        return qs.distinct()

    @action(detail=False, methods=["post"])
    def bulk_upload(self, request):
        """Upload multiple products at once, creating categories if missing."""
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of products"}, status=status.HTTP_400_BAD_REQUEST)

        created, errors = [], []

        for i, data in enumerate(request.data):
            serializer = ProductUploadSerializer(data=data)
            if serializer.is_valid():
                try:
                    category_names = serializer.validated_data.pop("category_names")
                    categories = []
                    for name in category_names:
                        category, _ = Category.objects.get_or_create(
                            name=name,
                            defaults={"slug": name.lower().replace(" ", "-")}
                        )
                        categories.append(category)

                    product = Product.objects.create(**serializer.validated_data)
                    product.categories.set(categories)
                    created.append(ProductSerializer(product).data)
                except Exception as e:
                    errors.append({"index": i, "error": str(e), "data": data})
            else:
                errors.append({"index": i, "errors": serializer.errors, "data": data})

        status_code = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response({
            "created_count": len(created),
            "error_count": len(errors),
            "created_products": created,
            "errors": errors,
        }, status=status_code)
