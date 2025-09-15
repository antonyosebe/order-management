from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Customer(AbstractUser):
 
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Enter a valid phone number. Example: 0700000000"
    )

    phone = models.CharField(
        max_length=17,
        validators=[phone_regex],
        blank=True
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.TextField(blank=True)

    openid_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
