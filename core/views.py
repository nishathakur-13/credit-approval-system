from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
import math
from datetime import date, timedelta


# ----------------- HELPER FUNCTION -----------------

def calculate_credit_score(customer_id):
    """A simple credit score calculation."""
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return 0

    past_loans = Loan.objects.filter(customer=customer)
    
    emis_paid_on_time_count = sum(loan.emis_paid_on_time for loan in past_loans)
    num_loans_taken = past_loans.count()
    current_debt = sum(loan.loan_amount for loan in past_loans if loan.end_date > date.today())
    
    score = 50
    if current_debt > customer.approved_limit:
        score = 0

    if num_loans_taken > 5:
        score += 10

    if emis_paid_on_time_count > 50:
        score += 15

    return min(score, 100)

# ----------------- API VIEWS -----------------

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class LoanListView(generics.ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')
        monthly_salary = data.get('monthly_salary')
        phone_number = data.get('phone_number')

        approved_limit = round(36 * monthly_salary, -5)

        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                monthly_salary=monthly_salary,
                phone_number=phone_number,
                approved_limit=approved_limit
            )
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityView(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        try:
            customer = Customer.objects.get(id=customer_id)
            credit_score = calculate_credit_score(customer_id)
            
            current_loans = Loan.objects.filter(customer=customer, end_date__gt=date.today())
            sum_of_current_emis = sum(loan.monthly_repayment for loan in current_loans)

            approval = False
            corrected_interest_rate = interest_rate

            if credit_score > 50:
                approval = True
            elif 50 >= credit_score > 30:
                corrected_interest_rate = max(interest_rate, 12.0)
                approval = True
            elif 30 >= credit_score > 10:
                corrected_interest_rate = max(interest_rate, 16.0)
                approval = True
            else:
                approval = False

            new_monthly_installment = (loan_amount * (1 + (corrected_interest_rate / 100))) / tenure
            if (sum_of_current_emis + new_monthly_installment) > (0.5 * customer.monthly_salary):
                approval = False

            response_data = {
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate if approval else None,
                'tenure': tenure,
                'monthly_installment': round(new_monthly_installment, 2) if approval else None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CreateLoanView(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        try:
            customer = Customer.objects.get(id=customer_id)
            credit_score = calculate_credit_score(customer_id)
            current_loans = Loan.objects.filter(customer=customer, end_date__gt=date.today())
            sum_of_current_emis = sum(loan.monthly_repayment for loan in current_loans)

            approval = False
            if credit_score > 50:
                approval = True
            
            new_monthly_installment = (loan_amount * (1 + (interest_rate / 100))) / tenure
            if (sum_of_current_emis + new_monthly_installment) > (0.5 * customer.monthly_salary):
                approval = False

            if approval:
                new_loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=interest_rate,
                    tenure=tenure,
                    monthly_repayment=round(new_monthly_installment, 2),
                    emis_paid_on_time=0,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=tenure * 30)
                )
                
                response_data = {
                    'loan_id': new_loan.id,
                    'customer_id': customer.id,
                    'loan_approved': True,
                    'monthly_installment': new_loan.monthly_repayment
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    'loan_id': None,
                    'customer_id': customer.id,
                    'loan_approved': False,
                    'message': "Loan not approved based on eligibility criteria."
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

# --- ADD THESE NEW VIEWS AT THE END ---

class ViewLoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'id' # Specify that we are looking up by loan 'id'

class ViewCustomerLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get_queryset(self):
        # Get the customer_id from the URL
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__id=customer_id)
        