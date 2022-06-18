from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


# def billing_profile_created_reciever(sender, instance, created, *args, **kwargs):
#     if created:
#         print("API REQUEST Send to stripe")
#         instance.customer_id = newID


def user_created_reciever(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(
            user=instance, email=instance.email)


post_save.connect(user_created_reciever, sender=User)
