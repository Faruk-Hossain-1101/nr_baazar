import os
import requests
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from shop.models.order import Order
from shop.models.customer import Customer, Coupon, CustomerCoupon

@receiver(post_save, sender=Order)
def after_order_create_coustomer_reply(sender, instance, created, **kwargs):
    """Automatically creates a Profile instance when a User is created."""
    if not created:
        return

    # Fetch WhatsApp API token from environment variables (security best practice)
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    if not WHATSAPP_ACCESS_TOKEN:
        print("ERROR: WhatsApp API token is missing!")
        return  # Exit if token is not set

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Check if the order qualifies for a coupon
    if instance.total_amount >= 2000:
        customer_coupon = CustomerCoupon.objects.filter(customer=instance.customer).first()
        expiry_date = now() + timedelta(days=90)
        uuid_id = f"SAVE10-{str(uuid.uuid4())[:6].upper()}"

        if customer_coupon:
            customer_coupon.is_used = False
            # Update existing coupon
            coupon = customer_coupon.coupon
            coupon.expiry_date = expiry_date
            coupon.code = uuid_id
            coupon.is_active = True  # Ensure coupon is active
            coupon.save()
            customer_coupon.save()
        else:
            # Create a new coupon
            coupon = Coupon.objects.create(
                code=uuid_id,
                discount_type="percentage",
                discount_amount=10,
                max_discount=500,
                minium_order=2000,
                expiry_date=expiry_date,
                coupon_type="individual",
            )
            CustomerCoupon.objects.create(customer=instance.customer, coupon=coupon, is_used=False)

        # Extract coupon details
        code = coupon.code
        max_discount = coupon.max_discount
        min_price = coupon.minium_order
        formatted_expiry_date = expiry_date.strftime("%Y-%m-%d")  # Convert to readable format

        discount_text = (
            f"Save {coupon.discount_amount}% up to Rs.{max_discount}"
            if coupon.discount_type == "percentage"
            else f"Save flat Rs.{max_discount}"
        )

        # WhatsApp API Payload
        data = {
            "messaging_product": "whatsapp",
            "to": f"91{instance.customer.phone}",
            "type": "template",
            "template": {
                "name": "after_order",
                "language": {"code": "en_US"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            { "type": "text", "parameter_name": "customer_name", "text": instance.customer.name },       
                            { "type": "text", "parameter_name": "order_number", "text": instance.order_number },    
                            { "type": "text", "parameter_name": "coupon", "text": code },        
                            { "type": "text", "parameter_name": "discount", "text": discount_text }, 
                            { "type": "text", "parameter_name": "min_price", "text": f"Rs.{min_price}" },        
                            { "type": "text", "parameter_name": "expire_date", "text": formatted_expiry_date }    
                        ],
                    }
                ],
            },
        }

        # Send WhatsApp notification
        response = requests.post(
            "https://graph.facebook.com/v21.0/202708459602859/messages",
            headers=headers,
            json=data,
        )

        # Log API response
        if response.status_code == 200:
            print(f"WhatsApp message sent successfully to {instance.customer.phone}")
        else:
            print(f"Failed to send WhatsApp message: {response.text}")

    else:
        # Handle used coupons
        if hasattr(instance, "coupon") and instance.coupon:
            customer_coupon = CustomerCoupon.objects.filter(coupon=instance.coupon).first()
            if customer_coupon:
                customer_coupon.is_used = True
                customer_coupon.coupon.is_active = False
                customer_coupon.coupon.save()
                customer_coupon.save()

        print("Order created successfully!")
