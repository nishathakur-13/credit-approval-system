from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
import math
from datetime import date, timedelta

# ----------------- HELPER FUNCTIONS -----------------

def calculate_emi(principal, annual_rate, tenure):
    """Calculates EMI using the Reducing Balance (Compound Interest) formula."""
    if annual_rate == 0:
        return round(principal / tenure, 2)
    
    r = (annual_rate / 12) / 100
    numerator = principal * r * math.pow(1 + r, tenure)
    denominator = math.pow(1 + r, tenure) - 1
    emi = numerator / denominator
    return round(emi, 2)

def calculate_credit_score(customer_id):
    """A simple credit score calculation based on loan history."""
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

# ----------------- AUTHENTICATION VIEWS -----------------

def unified_login(request):
    """Handles the Sign In portal with role-based routing."""
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('/register-ui/')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login.html')

def signup_view(request):
    """Handles new Customer account creation."""
    if request.method == "POST":
        u_name = request.POST.get('username')
        email = request.POST.get('email')
        p_word = request.POST.get('password')
        
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')
        
        # Create standard user (not staff)
        User.objects.create_user(username=u_name, email=email, password=p_word)
        messages.success(request, "Account created successfully! Please sign in.")
        return redirect('login-gateway')
        
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login-gateway')

# ----------------- UI / FRONTEND VIEW -----------------

def register_customer_page(request):
    """Handles the Frontend UI for Customer Registration."""
    if not request.user.is_authenticated:
        return redirect('login-gateway')

    if request.method == "POST":
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            age = int(request.POST.get('age'))
            monthly_income = int(request.POST.get('monthly_income'))
            phone_number = request.POST.get('phone_number')

            approved_limit = round(36 * monthly_income, -5)

            new_customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                monthly_salary=monthly_income,
                approved_limit=approved_limit,
                phone_number=phone_number
            )

            return render(request, 'register.html', {
                "success": True,
                "limit": f"{approved_limit:,}",
                "name": first_name
            })
        except Exception as e:
            return render(request, 'register.html', {"error": str(e)})

    return render(request, 'register.html')

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
            interest_rate = float(data.get('interest_rate'))
            tenure = int(data.get('tenure'))

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
                    tenure=tenure,
                    monthly_repayment=final_emi,
                    emis_paid_on_time=0,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=tenure * 30)
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

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewLoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'id'

class ViewCustomerLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__id=customer_id)