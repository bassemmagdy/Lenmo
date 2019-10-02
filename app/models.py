# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    balance = models.FloatField(default=0, null=False)


class Loan(BaseModel):
    borrower = models.ForeignKey('app.User', on_delete=models.CASCADE, null=False)
    period = models.IntegerField(validators=[MinValueValidator(1)], null=False)
    amount = models.FloatField(validators=[MinValueValidator(1)], null=False)
    loan_status = (
        (1, ('Pending')),
        (2, ('Funded')),
        (3, ('Completed')),
    )
    status = models.IntegerField(choices=loan_status, default=1)


class Offer(BaseModel):
    investor = models.ForeignKey('app.User', null=False, on_delete=models.CASCADE)
    loan = models.ForeignKey(
        'app.Loan',
        null=False,
        on_delete=models.CASCADE,
        related_name='offers')
    interest_rate = models.FloatField(
        validators=[MinValueValidator(1.0)], null=False)
    offer_status = (
        (1, ('Pending')),
        (2, ('Rejected')),
        (3, ('Accepted')),
    )
    status = models.IntegerField(choices=offer_status, default=1)

    class Meta:
        unique_together = ('investor', 'loan'),


class Payment(BaseModel):
    
    installment = models.FloatField(null=False)
    borrower = models.ForeignKey('app.User',
                                 null=False,
                                 on_delete=models.CASCADE,
                                 related_name='borrower')
    lender = models.ForeignKey('app.User',
                               null=False,
                               on_delete=models.CASCADE,
                               related_name='lender')
    due_date = models.DateField(null=False)
    payment_status = (
        (1, ('Pending')),
        (2, ('Confirmed'))
    )
    status = models.IntegerField(choices=payment_status, default=1)
