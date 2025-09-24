import logging
from celery import shared_task
from .utils import NotificationService
from orders.models import Order
from customers.models import Customer

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_order_sms_task(self, order_id: int):
    """
    Send SMS notification to customer when an order is placed.
    """
    try:
        order = Order.objects.get(id=order_id)
        success = NotificationService.send_order_sms(order)

        if success:
            logger.info(f"SMS sent successfully for order {order_id}")
            return True
        else:
            logger.error(f"SMS sending failed for order {order_id}")
            return False

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found. SMS not sent.")
        return False
    except Exception as e:
        logger.error(f"Error sending SMS for order {order_id}: {e}")
        if not self.request.is_eager:  
            raise self.retry(exc=e, countdown=60)
        return False

@shared_task(bind=True, max_retries=3)
def send_admin_email_task(self, order_id: int):
    """
    Send email notification to admin when a new order is placed.
    """
    try:
        order = Order.objects.get(id=order_id)
        success = NotificationService.send_order_email_to_admin(order)

        if success:
            logger.info(f"Admin email sent successfully for order {order_id}")
            return True
        else:
            logger.error(f"Admin email sending failed for order {order_id}")
            return False

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found. Admin email not sent.")
        return False
    except Exception as e:
        logger.error(f"Error sending admin email for order {order_id}: {e}")
        if not self.request.is_eager:
            raise self.retry(exc=e, countdown=60)
        return False


@shared_task
def send_welcome_email_task(customer_id: int):
    """
    Send a welcome email to a new customer.
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        success = NotificationService.send_welcome_email(customer)

        if success:
            logger.info(f"Welcome email sent to customer {customer.email}")
            return True
        else:
            logger.error(f"Welcome email sending failed for customer {customer_id}")
            return False

    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found. Welcome email not sent.")
        return False
    except Exception as e:
        logger.error(f"Error sending welcome email for customer {customer_id}: {e}")
        return False
