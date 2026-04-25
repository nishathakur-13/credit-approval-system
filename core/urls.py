from django.urls import path
from .views import (
    register_customer_page, 
    RegisterCustomerView, 
    CheckEligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewCustomerLoansView,
    CustomerListView,
    LoanListView
)

urlpatterns = [
    # This is what /register-ui/ and /api/ look for internally
    path('', register_customer_page, name='register_ui'), 
    path('register/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-customer/<int:id>/', CustomerListView.as_view(), name='view-customer'), 
    path('view-loan/<int:id>/', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='view-customer-loans'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('loans/', LoanListView.as_view(), name='loan-list'),
]