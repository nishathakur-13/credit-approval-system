from django.urls import path
from django.shortcuts import render # Added this import for the dashboard lambda
from .views import (
    RegisterCustomerView, 
    CheckEligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewCustomerLoansView,
    signup_view 
)

urlpatterns = [
    # 1. API Endpoints (Assignment Requirements)
    path('api/register/', RegisterCustomerView.as_view(), name='api-register'),
    path('api/check-eligibility/', CheckEligibilityView.as_view(), name='api-check-eligibility'),
    path('api/create-loan/', CreateLoanView.as_view(), name='api-create-loan'),
    path('api/view-loan/<int:id>/', ViewLoanDetailView.as_view(), name='api-view-loan'),
    path('api/view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='api-view-customer-loans'),

    # 2. UI Pages (The Professional Frontend)
    path('signup/', signup_view, name='register-ui'), # Changed to 'signup' to avoid collision
    path('dashboard/', lambda r: render(r, 'dashboard.html'), name='dashboard'),
]