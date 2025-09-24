from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.task import send_order_sms_task, send_admin_email_task
from django.conf import settings
from notifications.utils import NotificationService 
from django.db import transaction


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    if not created or instance.total_amount <= 0:
        return  

    def send_notifications():
        if getattr(settings, "DEBUG", False):
            send_order_sms_task(instance.id)
            send_admin_email_task(instance.id)
        else:
            send_order_sms_task.delay(instance.id)
            send_admin_email_task.delay(instance.id)

    transaction.on_commit(send_notifications)
