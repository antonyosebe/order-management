from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'address',
            'is_active',
        ]
        read_only_fields = ['id', 'is_active']


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'address',
            'password',
        ]

    def create(self, validated_data):
        # use set_password to hash the password
        password = validated_data.pop("password")
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer
