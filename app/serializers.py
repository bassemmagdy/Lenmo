# from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Loan, Offer, User, Payment
from rest_framework.serializers import CurrentUserDefault, HiddenField


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = 'id', 'username', 'password', 'email',
        extra_kwargs = {'password': {'write_only': True}}


class UserRegisterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'email', 'password', 'username',
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'username': {'required': False},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={
            'input_type': 'password'},
        trim_whitespace=False)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        else:
            raise serializers.ValidationError(
                'Please Recheck Your Credentials')


class LoanSerializer(serializers.ModelSerializer):
    borrower = UserSerializer()

    class Meta:
        model = Loan
        fields = '__all__'


class DestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = 'id',


class CreateLoanSerializer(serializers.ModelSerializer):
    borrower = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Loan
        exclude = 'status', 'created', 'updated',


class UpdateLoanSerializer(serializers.ModelSerializer):

    def validate(self, data):
        offer_list = Offer.objects.filter(loan__id=self.instance.id)
        if offer_list:
            for offer in offer_list:
                if offer.status == 3:
                    raise serializers.ValidationError("Sorry You are not allowed to edit while having accepted offers!")
        return data

    class Meta:
        model = Loan
        exclude = 'borrower', 'created', 'updated', 'status',


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'


class CreateOfferSerializer(serializers.ModelSerializer):
    investor = HiddenField(default=CurrentUserDefault())
    
    def validate(self, data):
        if self.context['request'].user == data.get('loan').borrower:
            raise serializers.ValidationError("Sorry you are not allowed to bid over your own loan!")

        offer_list = Offer.objects.filter(status=3)
        for offer in offer_list:
            if offer.status == 3:
                raise serializers.ValidationError("Sorry you are not allowed to bid over a funded loan!")

        if self.context['request'].user.balance < data.get('loan').amount + 3:
            raise serializers.ValidationError("Sorry you don't have enough balance to fund this loan!")
        return data

    class Meta:
        model = Offer
        exclude = 'status', 'created', 'updated',


class UpdateOfferSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if self.instance.staus != 1:
            raise serializers.ValidationError("Sorry You are not allowed to update accepted offers!")

    class Meta:
        model = Loan
        exclude = 'investor', 'created', 'updated', 'status',


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = 'borrower', 'lender', 'installment', 'due_date', 'id', 'created', 'updated',