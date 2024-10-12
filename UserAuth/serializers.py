from rest_framework import serializers
from .models import User
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util
import os
from CompanyManagement.serializers import CompanySerializer
from CompanyManagement.models import Company

# User Profile
class UserRegistrationsSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    name=serializers.CharField(required=True)
    role=serializers.CharField(required=True)
    company=serializers.CharField(required=True)
    password=serializers.CharField(write_only=True,required=True)
    password2=serializers.CharField(write_only=True,required=True)
    
    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        if password != password2:
            return serializers.ValidationError('Password does not match')
        return attrs
    
    def create(self,validated_data):
        company_id=validated_data['company']
        
        try:
            company_instance=Company.objects.get(pk=int(company_id))
        except Company.DoesNotExist:
            raise serializers.ValidationError('Invalid company ID provided.')    
        
        user=User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            role=validated_data['role'],
            company=company_instance,
            password=validated_data['password']
        )
        return user

# User Login
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=100)
    class Meta:
        model=User
        fields=['email','password']
        
# User Profile View
class UserProfileSerializer(serializers.ModelSerializer):
    company=CompanySerializer(read_only=True)
    
    class Meta:
        model=User
        fields=['id','name','role','company']
        
# Change Password
class UserChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(max_length=100,style={'input_type':'password'},write_only=True)
    new_password=serializers.CharField(max_length=100,style={'input_type':'password'})
    conform_password=serializers.CharField(max_length=100,style={'input_type':'password'},write_only=True)
    
    class Meta:
        fields=['old_password','new_password','conform_password']
        
    def validate(self,attrs):
        user=self.context.get('user')
        
        old_password=attrs.get('old_password')
        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})
        
        new_password=attrs.get('new_password')
        conform_password=attrs.get('conform_password')
        if new_password != conform_password:
            raise ValueError('Password and Confirm Password does not match')
        
        if old_password == new_password:
            raise serializers.ValidationError({'new_password': 'New password cannot be the same as the old password.'})
        
        user.set_password(new_password)
        user.save() 
        return attrs
    
# Send Reset Email
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=100)
    class Meta:
        fields=['email']
        
    def validate(self,attrs):
        email=attrs.get('email')
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            uid=urlsafe_base64_encode(force_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:8000/api/user/reset/'+uid+'/'+token
            print('Password Reset Link', link)
            # Send Email
            body='Click Following Link to Reset Your Password '+link
            data={
                'subject':'Reset Your Password',
            'body':body,
            'to_email':user.email}
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')
        
# Password Reset
class UserPasswordResetSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=100,style={'input_type':'password2'},write_only=True)
    class Meta:
        fields=['password','password2']
        
    def validate(self,attrs):
        try:
            password=attrs.get('password')
            password2=attrs.get('password2')
            uid=self.context.get('uid')
            token=self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            id=smart_str(urlsafe_base64_decode(uid))
            user=User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError('Token is not Valid or Expired')