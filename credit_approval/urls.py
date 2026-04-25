from django.urls import path
from .views import (
    RegisterCustomerView, 
    CheckEligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewCustomerLoansView,
    CustomerListView # This is the one we'll use for viewing a customer
)

urlpatterns = [
    # Assignment Endpoints
    path('register/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    
    # --- The Fix for your 404 ---
    # This maps 'view-customer/1/' to your Customer list logic
    path('view-customer/<int:id>/', CustomerListView.as_view(), name='view-customer'), 
    
    path('view-loan/<int:id>/', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='view-customer-loans'),
    
    # Utility list views
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('loans/', LoanListView.as_view(), name='loan-list'),
]