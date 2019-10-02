from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnlyLoan(BasePermission):
    message = 'Sorry only owner allowed to edit or delete!'

    def has_object_permission(self, request, view, obj):
        return obj.borrower == request.user


class IsOwnerOrReadOnlyOffer(BasePermission):
    message = 'Sorry only owner allowed to edit or delete!'

    def has_object_permission(self, request, view, obj):
        return obj.investor == request.user


# payment view or update
class CanPay(BasePermission):
    message = 'Sorry only lender can pay his bills!!'

    def has_object_permission(self, request, view, obj):
        return obj.borrower == request.user
