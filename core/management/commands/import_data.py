import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Customer, Loan

class Command(BaseCommand):
    help = 'Deletes all existing data and imports new data from Excel files'

    def handle(self, *args, **kwargs):
        # --- Clear all old data first ---
        self.stdout.write(self.style.WARNING('Clearing existing database tables...'))
        Loan.objects.all().delete()
        Customer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Database cleared.'))

        # --- Import Customer Data ---
        self.stdout.write('Importing customer data...')
        try:
            customer_df = pd.read_excel('customer_data.xlsx')
            for index, row in customer_df.iterrows():
                Customer.objects.create(
                    id=row['Customer ID'],
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    age=row['Age'],
                    phone_number=row['Phone Number'],
                    monthly_salary=row['Monthly Salary'],
                    approved_limit=row['Approved Limit'],
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported customer data.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing customer data: {e}'))
            return

        # --- Import Loan Data ---
        self.stdout.write('Importing loan data...')
        try:
            loan_df = pd.read_excel('loan_data.xlsx')
            for index, row in loan_df.iterrows():
                try:
                    customer = Customer.objects.get(id=row['Customer ID'])

                    # Use get_or_create to prevent errors with duplicate Loan IDs
                    Loan.objects.get_or_create(
                        id=row['Loan ID'],
                        defaults={
                            'customer': customer,
                            'loan_amount': row['Loan Amount'],
                            'tenure': row['Tenure'],
                            'interest_rate': row['Interest Rate'],
                            'monthly_repayment': row['Monthly payment'],
                            'emis_paid_on_time': row['EMIs paid on Time'],
                            'start_date': row['Date of Approval'],
                            'end_date': row['End Date'],
                        }
                    )
                except Customer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Customer with ID {row['Customer ID']} not found. Skipping loan {row['Loan ID']}."))
            self.stdout.write(self.style.SUCCESS('Successfully imported loan data.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing loan data: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('All data imported successfully!'))