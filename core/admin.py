from django.contrib import admin
from .models import Customer, Loan

# --- Customizing the Admin Interface Design ---
admin.site.site_header = "Credit System Control Center"  # Login page and top header
admin.site.index_title = "Operational Data Management"    # Main dashboard subtitle
admin.site.site_title = "Nisha's Credit Portal"          # Browser tab title

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = ('id', 'first_name', 'last_name', 'monthly_salary', 'approved_limit')
    
    # Adding a search bar for easy data lookup
    search_fields = ('first_name', 'last_name', 'phone_number')
    
    # Makes the ID link directly to the edit page
    list_display_links = ('id', 'first_name')
    
    # Ordering data by ID (newest or specific order)
    ordering = ('id',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    # Showing customer name alongside loan details
    list_display = ('id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'monthly_repayment')
    
    # Filters on the right sidebar to drill down into data
    list_filter = ('interest_rate', 'tenure')
    
    # Search by Loan ID or Customer Name
    search_fields = ('id', 'customer__first_name', 'customer__last_name')
    
    list_display_links = ('id', 'customer')