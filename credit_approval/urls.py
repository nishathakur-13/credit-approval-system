from django.contrib import admin
from django.urls import path, include
from core.views import unified_login, logout_view, signup_view # Make sure signup_view is here

urlpatterns = [
    # 1. Landing Page
    path('', unified_login, name='login-gateway'),

    # 2. THE MISSING LINK: Signup Page
    path('signup/', signup_view, name='signup'),

    # 3. Logout
    path('logout/', logout_view, name='logout'),

    # 4. Admin
    path('admin/', admin.site.urls),
    
    # 5. App Routes
    path('register-ui/', include('core.urls')),
    path('api/', include('core.urls')),
]