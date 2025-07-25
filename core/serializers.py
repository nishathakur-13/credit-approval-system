from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        # Exclude fields that shouldn't be in nested responses if you want
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanSerializer(serializers.ModelSerializer):
    # This nests the customer details within the loan data
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'