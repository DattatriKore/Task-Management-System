from django.contrib import admin
from django.urls import path
from UserAuth.views import UserRegistrationView,UserLoginView,UserLogoutView,UserProfileView,UserChangePasswordView,SendPasswordResetEmailView, UserPasswordResetView

urlpatterns=[
    path('register/',UserRegistrationView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('profile/',UserProfileView.as_view()),
    path('profile/<int:pk>/',UserProfileView.as_view()),
    path('logout/',UserLogoutView.as_view()),
    path('changepassword/',UserChangePasswordView.as_view()),
    path('send-password-reset-email/',SendPasswordResetEmailView.as_view()),
    path('passwordreset/<uid>/<token>/',UserPasswordResetView.as_view()),
]