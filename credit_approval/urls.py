from django.contrib import admin
from django.urls import path, include
from core.views import unified_login, logout_view  # Boss needs to know how to log people in

urlpatterns = [
    # 1. The Landing Page (The Main Entrance)
    path('', unified_login, name='login-gateway'),

    # 2. Logout functionality
    path('logout/', logout_view, name='logout'),

    # 3. The Admin "Control Center"
    path('admin/', admin.site.urls),
    
    # 4. Routing for the Customer UI
    # This sends any request starting with 'register-ui/' to core/urls.py
    path('register-ui/', include('core.urls')),
    
    # 5. Routing for the Backend APIs
    # This sends any request starting with 'api/' to core/urls.py
    path('api/', include('core.urls')),
]