from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Wallet, Transaction


@receiver(post_save, sender=User)
def create_wallet(sender, **kwargs):
    if kwargs['created']:
        Wallet.objects.create(user=kwargs['instance'])
