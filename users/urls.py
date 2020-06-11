from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'), 
]