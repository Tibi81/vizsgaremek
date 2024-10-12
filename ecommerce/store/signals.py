from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer


'''
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        # Létrehoz egy Customer objektumot a felhasználóhoz, amikor egy új User jön létre
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()
'''


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        # Létrehoz egy Customer objektumot a felhasználóhoz a név és email mező kitöltésével
        Customer.objects.create(
            user=instance,
            name=instance.username,  # A név kitöltése a felhasználónévvel
            email=instance.email     # Az email kitöltése a felhasználó email címével
        )

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()