from django.urls import path
from .views import (
    RegisterCustomerView, 
    CheckEligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewCustomerLoansView,
    signup_view  # This matches the function name in views.py
)

urlpatterns = [
    # API Endpoints (Assignment Requirements)
    path('register/', RegisterCustomerView.as_view(), name='api-register'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='api-check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='api-create-loan'),
    path('view-loan/<int:id>/', ViewLoanDetailView.as_view(), name='api-view-loan'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='api-view-customer-loans'),

    # UI Pages
    path('register/', signup_view, name='register-ui'), # Changed from register_customer_page
]