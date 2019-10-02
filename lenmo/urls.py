from django.urls import path
from app.views import UserRegisterView, UserLoginView, LoanViewSet, OfferViewSet, accept_offer, PaymentView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('api/loan', LoanViewSet, basename='loan')
router.register('api/offer', OfferViewSet, basename='offer')
router.register('api/payment', PaymentView, basename='offer')

urlpatterns = [
    # Authentication
    path('api/register', UserRegisterView.as_view(), name='register'),
    path('api/login', UserLoginView.as_view(), name='login'),
    path('api/accept_offer/<int:offer>/', accept_offer, name='accept_offer'),

]


urlpatterns.extend(router.urls)
