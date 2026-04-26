from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta
import math

from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer

# ----------------- HELPER LOGIC -----------------

def calculate_emi(principal, annual_rate, tenure_months):
    """Calculates EMI using reducing balance compound interest."""
    if annual_rate == 0:
        return principal / tenure_months
    monthly_rate = (annual_rate / 12) / 100
    emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / \
          (math.pow(1 + monthly_rate, tenure_months) - 1)
    return round(emi, 2)

def calculate_credit_score(customer_id):
    """
    Placeholder for credit score logic. 
    In a real app, this would evaluate historical loan performance.
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        
        # Simple logic: 50 base + 5 for every loan paid on time
        score = 50
        for loan in loans:
            if loan.emis_paid_on_time > 0:
                score += 5
        return min(score, 100)
    except:
        return 0

# ----------------- AUTH & DASHBOARD VIEWS -----------------

def unified_login(request):
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            # Staff goes to Django Admin, regular users go to Customer UI
            return redirect('admin:index') if user.is_staff else redirect('dashboard')
        messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            salary = float(request.POST.get('salary', 0))
            limit = round(36 * salary, -5)
            
            user = form.save()
            Customer.objects.create(
                user=user, # Ensure your Customer model has a OneToOneField to User
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                age=int(request.POST.get('age', 0)),
                monthly_salary=salary,
                approved_limit=limit,
                phone_number=request.POST.get('phone_number')
            )
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Check details.")
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login-gateway')

# ----------------- API VIEWS (DRF) -----------------

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class LoanListView(generics.ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data
        try:
            monthly_salary = data.get('monthly_salary')
            approved_limit = round(36 * monthly_salary, -5)

            customer = Customer.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                age=data.get('age'),
                monthly_salary=monthly_salary,
                phone_number=data.get('phone_number'),
                approved_limit=approved_limit
            )
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityView(APIView):
    def post(self, request):
        data = request.data
        try:
            customer_id = data.get('customer_id')
            loan_amount = float(data.get('loan_amount'))
            interest_rate = float(data.get('interest_rate'))
            tenure = int(data.get('tenure'))

            customer = Customer.objects.get(id=customer_id)
            credit_score = calculate_credit_score(customer_id)
            
            current_loans = Loan.objects.filter(customer=customer, end_date__gt=date.today())
            sum_of_current_emis = sum(loan.monthly_repayment for loan in current_loans)

            approval = False
            corrected_interest_rate = interest_rate

            # Eligibility Slabs
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

            new_emi = calculate_emi(loan_amount, corrected_interest_rate, tenure)

            # Max EMI check (50% of salary)
            if (sum_of_current_emis + new_emi) > (0.5 * customer.monthly_salary):
                approval = False

            response_data = {
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate if approval else interest_rate,
                'tenure': tenure,
                'monthly_installment': new_emi if approval else 0
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CreateLoanView(APIView):
    def post(self, request):
        data = request.data
        try:
            customer_id = data.get('customer_id')
            loan_amount = float(data.get('loan_amount'))
            
            # Re-verify eligibility internally
            eligibility_response = CheckEligibilityView().post(request)
            eligibility_data = eligibility_response.data

            if eligibility_data.get('approval'):
                customer = Customer.objects.get(id=customer_id)
                final_rate = eligibility_data.get('corrected_interest_rate')
                final_emi = eligibility_data.get('monthly_installment')

                new_loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=final_rate,
                    tenure=data.get('tenure'),
                    monthly_repayment=final_emi,
                    emis_paid_on_time=0,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=int(data.get('tenure')) * 30)
                )
                
                return Response({
                    'loan_id': new_loan.id,
                    'customer_id': customer.id,
                    'loan_approved': True,
                    'monthly_installment': new_loan.monthly_repayment
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': "Loan not approved based on eligibility criteria."
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ViewLoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'id'

class ViewCustomerLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__id=customer_id)