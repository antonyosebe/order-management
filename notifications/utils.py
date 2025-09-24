import logging
import re
import unicodedata
from typing import List, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import africastalking

logger = logging.getLogger(__name__)


def clean_phone_number(phone: str) -> str:
    """Clean up a phone number: keep only digits and '+'."""
    phone = unicodedata.normalize("NFKC", phone)
    return re.sub(r"[^\d+]", "", phone)


def _get_sms_service() -> Optional[object]:
    """Try to initialize Africa's Talking SMS service."""
    try:
        username = settings.AFRICASTALKING_USERNAME
        api_key = settings.AFRICASTALKING_API_KEY
        sms = getattr(africastalking, "SMS", None)

    except Exception as e:
        logger.error("Failed to initialize SMS service: %s", e, exc_info=True)
        return None


#Service 
class NotificationService:
    """Send SMS and email notifications."""

    #SMS 
    @staticmethod
    def _send_sms(message: str, recipients: List[str]) -> bool:
        sms = _get_sms_service()

        if not sms and settings.AFRICASTALKING_USERNAME == "sandbox":
            logger.info("[Sandbox SMS] To=%s | Msg=%s", recipients, message)
            return True

        if not sms:
            logger.error("SMS service unavailable.")
            return False

        try:
            recipients = [clean_phone_number(r) for r in recipients if r]
            response = sms.send(message, recipients)
            logger.info("SMS API returned: %s", response)

            recipients_data = response.get("SMSMessageData", {}).get("Recipients", [])
            if recipients_data and recipients_data[0].get("status") == "Success":
                logger.info("SMS sent to %s successfully.", recipients)
                return True

            logger.error("SMS failed | Recipients=%s | Response=%s", recipients, response)
            return False

        except Exception as e:
            logger.error("Error sending SMS | Recipients=%s | %s", recipients, e, exc_info=True)
            return False

    #Email
    @staticmethod
    def _send_email(subject: str, recipient: str, template: str, context: dict) -> bool:
        try:
            html_msg = render_to_string(template, context)
            plain_msg = strip_tags(html_msg)

            send_mail(
                subject=subject,
                message=plain_msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_msg,
                fail_silently=False,
            )
            logger.info("Email sent | Recipient=%s | Subject=%s", recipient, subject)
            return True

        except Exception as e:
            logger.error("Failed to send email | Recipient=%s | %s", recipient, e, exc_info=True)
            return False

    #Notifications 
    @classmethod
    def send_order_sms(cls, order) -> bool:
        """Send order confirmation SMS to customer."""
        if order.total_amount <= 0:
            logger.info(f"Skipping SMS for order {order.order_number} because total is {order.total_amount}")
            return False

        phone = getattr(order.customer, "phone", None)
        if not phone:
            logger.error("Can't send SMS: Customer %s has no phone number.", order.customer.id)
            return False

        message = (
            f"Hi {order.customer.first_name},\n"
            f"Your order #{order.order_number} is confirmed!\n"
            f"Total: KES {order.total_amount}\n"
        )
        return cls._send_sms(message, [phone])

    @classmethod
    def send_order_email_to_admin(cls, order) -> bool:
        """Notify admin about a new order."""
        if order.total_amount <= 0:
            logger.info(f"Skipping admin email for order {order.order_number} because total is {order.total_amount}")
            return False
        subject = f"New Order Received - #{order.order_number}"
        context = {"order": order}
        admin_email = getattr(settings, "ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)
        return cls._send_email(subject, admin_email, "emails/order_notification.html", context)
