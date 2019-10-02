from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import Payment, Loan


@receiver(post_save, sender=Payment)
def on_change(sender, instance: Payment, created, update_fields, **kwargs):
    if not created:
        payment_list = Payment.objects.filter(borrower=instance.borrower, lender=instance.lender, status=1)
        if not payment_list.exists():
            Loan.objects.filter(borrower=instance.borrower, offers__investor=instance.lender).update(status=3)
