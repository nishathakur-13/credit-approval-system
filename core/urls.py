from django.urls import path
from .views import (
    CustomerListView,
    LoanListView,
    RegisterCustomerView,
    CheckEligibilityView,
    CreateLoanView,
    ViewLoanDetailView,
    ViewCustomerLoansView
)

urlpatterns = [
    # POST APIs
    path('register/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),

    # GET APIs for viewing specific data
    path('view-loan/<int:id>/', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='view-customer-loans'),

    # GET APIs for listing all data
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('loans/', LoanListView.as_view(), name='loan-list'),
]