from django.contrib import admin
from django.urls import path, include
from core.views import register_customer_page  # Import the new UI view

urlpatterns = [
    # The Branded Admin Panel
    path('admin/', admin.site.urls),
    
    # The Customer Registration Frontend (The UI Page)
    path('register-ui/', register_customer_page, name='register_ui'),
    
    # The Backend API Endpoints (The logic layer)
    path('api/', include('core.urls')),
]