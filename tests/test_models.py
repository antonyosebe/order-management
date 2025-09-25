import pytest
from django.core.exceptions import ValidationError
from customers.models import Customer


@pytest.mark.django_db
def test_create_customer_success():
    """Customer registration with valid data"""
    customer = Customer.objects.create_user(
        email="antony@example.com",
        username="antony",
        password="psw1234",
        first_name="Antony",
        last_name="Test",
        phone="0700000000",
        address="123 Street"
    )
    assert customer.email == "antony@example.com"
    assert customer.username == "antony"
    assert customer.check_password("psw1234") is True
    assert customer.full_name == "Antony Test"
    assert customer.address == "123 Street"

@pytest.mark.django_db
def test_customer_email_uniqueness():
    """Uniq email """
    Customer.objects.create_user(
        email="unique@example.com",
        username="user1",
        password="pass1234"
    )
    with pytest.raises(Exception): 
        Customer.objects.create_user(
            email="unique@example.com",
            username="user2",
            password="pass1234"
        )


