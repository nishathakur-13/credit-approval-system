# Credit Approval Backend System

This is a Django REST Framework project that provides an API for a credit approval system. It allows for registering customers, checking loan eligibility, and creating loans based on historical data.

## Setup and Installation

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Load initial data: `python manage.py import_data`
7. Run the server: `python manage.py runserver`

## API Endpoints

* `POST /api/register/`: Register a new customer.
* `POST /api/check-eligibility/`: Check if a customer is eligible for a loan.
* `POST /api/create-loan/`: Create a new loan if the customer is eligible.
* `GET /api/view-loan/<id>/`: View details of a specific loan.
* `GET /api/view-loans/<customer_id>/`: View all loans for a specific customer.
