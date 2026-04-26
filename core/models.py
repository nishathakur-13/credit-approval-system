from django.db import models

class Customer(models.Model):
    """
    Stores customer personal and financial data.
    Linked to Loan model via ForeignKey.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.id})"


class Loan(models.Model):
    """
    Stores historical and current loan data.
    Uses FloatField for precision in interest and repayment calculations.
    """
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan #{self.id} - {self.customer.first_name}"