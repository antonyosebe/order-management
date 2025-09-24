from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('customer').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        # assign current user as customer
        serializer.save(customer=self.request.user)

    def update(self, request, *args, **kwargs):
        # prevent customers from changing customer field
        instance = self.get_object()
        if not request.user.is_staff and instance.customer != request.user:
            return Response({'error': 'You cannot edit this order.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # customers should not delete their own orders
        instance = self.get_object()
        if not request.user.is_staff and instance.customer == request.user:
            return Response({'error': 'You cannot delete your own order.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
