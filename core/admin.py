from django.contrib import admin
from .models import Customer, Loan

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'monthly_salary', 'approved_limit')
    search_fields = ('first_name', 'last_name', 'phone_number')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'loan_amount', 'interest_rate', 'tenure')
    list_filter = ('interest_rate',)