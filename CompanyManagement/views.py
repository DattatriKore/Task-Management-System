from django.shortcuts import render
from .models import Company
from .serializers import CompanySerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status,viewsets
from UserAuth.models import User

# Create your views here.

# Get Create Company
class CompanyGetCreateView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        if user.is_superuser:
            company=Company.objects.all()
        else:
            company=Company.objects.filter(user=user)
        serializer=CompanySerializer(company,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        user=request.user
        if user.is_superuser:
            serializer=CompanySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
# Company Retrieve Update Delete View
class CompanyRetrieveUpdateDeleteView(APIView):
    def get(self, request, pk):
        user = request.user
        company = None  
        if user.is_superuser:
            try:
                company = Company.objects.get(pk=pk) 
            except Company.DoesNotExist:
                return Response({"detail": "Company not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            company = Company.objects.filter(user=user, pk=pk).first() 
            if not company:
                return Response({"detail": "Company not found."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CompanySerializer(company)
        return Response(serializer.data)


    def patch(self,request,pk):
        user=request.user
        if user.is_superuser:
            company=Company.objects.get(pk=pk)
            serializer=CompanySerializer(company,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
    def delete(self,request,pk):
        user=request.user
        if user.is_superuser:
            company=Company.objects.get(pk=pk)
            company.delete()
            return Response({'massage':'Delete SuccessFully'})
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
