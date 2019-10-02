# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .serializers import UserRegisterationSerializer, UserSerializer, UserLoginSerializer, LoanSerializer, CreateLoanSerializer, OfferSerializer, UpdateLoanSerializer, DestroySerializer, CreateOfferSerializer, UpdateOfferSerializer, PaymentSerializer
from rest_framework.generics import CreateAPIView
from knox.models import AuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from rest_framework import generics
from .models import Loan, Offer, User, Payment
from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOrReadOnlyLoan, IsOwnerOrReadOnlyOffer, CanPay
from rest_framework.decorators import api_view
from django.core import serializers
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Q

# Create your views here.


class UserRegisterView(CreateAPIView):
    serializer_class = UserRegisterationSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        """
        Create customer and return Auth token of this user
        and create default patient to thi user.
        :return: Auth Token
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = AuthToken.objects.create(user)
        user_data = UserSerializer(
            user, context=self.get_serializer_context()).data
        return Response({
            "user": user_data,
            "token": token[-1]
        }, status=HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = AuthToken.objects.create(user)
        user_data = UserSerializer(
            user, context=self.get_serializer_context()).data
        return Response({
            "user": user_data,
            "token": token[-1]
        }, status=HTTP_200_OK)


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyLoan]

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateLoanSerializer
        return super(LoanViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = UpdateLoanSerializer
        return super(LoanViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.serializer_class = DestroySerializer
        return super(LoanViewSet, self).update(request, *args, **kwargs)


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyOffer, ]

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateOfferSerializer
        return super(OfferViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = UpdateOfferSerializer
        return super(OfferViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.serializer_class = DestroySerializer
        return super(LoanViewSet, self).destroy(request, *args, **kwargs)


class PaymentView(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def list(self, request, *args, **kwargs):
        self.queryset.filter(Q(borrower=request.user) | Q(lender=request.user))
        return super(PaymentView, self).list(request, args, kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = [CanPay, ]
        return super(PaymentView, self).update(request, args, kwargs)


# update status of loan also update user balance
def update_lone_and_user_balance(offer):
    user = User.objects.filter(pk=offer[0].investor.pk)
    # subtracting amount + lenmo balance
    new_balance = user[0].balance - offer[0].loan.amount - 3
    user.update(balance=new_balance)
    loan = Loan.objects.filter(id=offer[0].loan.pk)
    loan.update(status=2)
    return user


# schedule payment tasks after accepting offer
def schedule_payment_task(instance):
    amount = instance.loan.amount
    # refer to period in months and number of payments
    period = instance.loan.period
    interest_rate = instance.interest_rate
    # interest rate per payment
    period_rate = interest_rate / period / 100
    # extra money paid as interest on loan
    loan_cost = period_rate * amount / (1 - (1 + period_rate)**-period)
    single_payment = (loan_cost + amount) / period
    target_time = date.today() + relativedelta(months=+1)

    for i in range(0, period):
        Payment.objects.get_or_create(
            lender=instance.investor,
            borrower=instance.loan.borrower,
            installment=single_payment,
            due_date=target_time)
        target_time += relativedelta(months=+1)


# accept offer API
@api_view(['POST'])
def accept_offer(request, offer: int):
    offer = Offer.objects.filter(pk=offer)
    # check if any accepted offers for the loan
    if offer.exists():
        offer_list = Offer.objects.filter(id=offer[0].loan.pk, status=3)

        if offer_list.exists():
            return Response({"message": "Your loan is already Funded!"}, status=HTTP_400_BAD_REQUEST)

        # if user accepting offer is the object owner
        if offer[0].loan.borrower == request.user:
            # if offer's status is pending
            if offer[0].status == 1:
                # if lender doesn't have enough money for loan and fees
                if offer[0].investor.balance < offer[0].loan.amount + 3:
                    return Response({"message": "Sorry the investor doesn't have enough money!"},
                                    status=HTTP_400_BAD_REQUEST)
                else:
                    # update status of offer and loan also update user balance

                    offer.update(status=3)
                    update_lone_and_user_balance(offer)
                    offer_response = serializers.serialize('json', offer)
                    schedule_payment_task(offer[0])
                    return Response({
                        "offer": offer_response,
                        "message": "Offer Accepted",

                    }, status=HTTP_200_OK)
            else:
                return Response({"message": "You already Accepted or rejected that offer!"},
                                status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Sorry only loan's owner is allowed to accept the offer!"},
                            status=HTTP_403_FORBIDDEN)
    else:
        return Response({"message": "Object Not Found"}, status=HTTP_404_NOT_FOUND)
