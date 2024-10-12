from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate,logout
import os
from django.conf import settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserRegistrationsSerializer,UserLoginSerializer,UserProfileSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer

# Generate Token Manually
def get_token_for_user(user):
    refresh=RefreshToken.for_user(user)
    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token),
    }

# User Profile Registration 
class UserRegistrationView(APIView):
    def post(self,request,format=None):
        email=request.data['email']
        role=request.data['role']
        company=request.data['company']
        user_instance=User.objects.filter(email=email)
        if user_instance:
            return Response({'error':'User with given email already exists'})
        else:
            serializer=UserRegistrationsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user=serializer.save()
                return Response({'massage':'Registration Successfull'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
# User Login
class UserLoginView(APIView):
    def post(self,request,format=None):
        serializer=UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.data.get('email')
        password=serializer.data.get('password')
        user = authenticate(email=email,password=password)
        if user is not None:
            role=user.role
            token=get_token_for_user(user)
            return Response({'token':token, 'role':role,'massage':'Login SuccessFully'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or password is not valid']}},status=status.HTTP_404_NOT_FOUND)
        
# User Logout
class UserLogoutView(APIView):
    def post(self,request):
        token=request.headers.get('Authorization')
        if token:
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    
# User Profile View
class UserProfileView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    
    def get(self,request,format=None):
        serializer=UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def patch(self,request,pk):
        profile=User.objects.get(pk=pk)
        serializer=UserProfileSerializer(profile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
# User Change Password
class UserChangePasswordView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    
    def post(self,request,format=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'massage':'Change password SuccessFully'}, status=status.HTTP_200_OK)
    
# Send Password Reset Email
class SendPasswordResetEmailView(APIView):
    permission_classes=[AllowAny]
    
    def post(self,request,format=None):
        serializer=SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# User Password Reset
class UserPasswordResetView(APIView):
    permission_classes=[AllowAny]
    
    def post(self,request,uid,token,format=None):
        serializer=UserPasswordResetSerializer(data=request.data,context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)