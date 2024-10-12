from django.shortcuts import render
from datetime import timedelta
from .models import Category,Task,TaskAssignment
from datetime import date
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework import viewsets,status
from .serializers import CategorySerializer,TaskSerializer,TaskAssignSerializer
from UserAuth.models import User
from .permission import IsAdminOrManager,IsAdmin,IsEmployee,IsManager
from CompanyManagement.models import Company
import csv
from io import TextIOWrapper
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from django.core.management.base import BaseCommand

# Categories Get Create View
class CategoriesGetCreateView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        category=Category.objects.all()
        serializer=CategorySerializer(category,many=True)
        return Response(serializer.data)
            
    def post(self,request):
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

# Categories Retrieve Update DeleteView View
class CategoriesRetrieveUpdateDeleteView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, pk):
        category=Category.objects.get(pk=pk)
        serializer=CategorySerializer(category)
        return Response(serializer.data)
    
    def patch(self,request,pk):
        category=Category.objects.get(pk=pk)
        serializer=CategorySerializer(category,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
        
    def delete(self,request,pk):
        category=Category.objects.get(pk=pk)
        category.delete()
        return Response({'massage':'delete successfully'})

# Task Get Create View
class TaskGetCreateView(APIView):
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticatedOrReadOnly()]
        elif self.request.method=='POST':
            return [IsAdminOrManager()]
        return super().get_permissions()
        
    def get(self,request):
        task=Task.objects.all()
            
        # Filtering
        category_id=request.query_params.get('category',None)
        company_id=request.query_params.get('company',None)
        if category_id:
            task=Task.objects.filter(category_id=category_id)
        if company_id:
            task=Task.objects.filter(company_id=company_id)
                
        # Sorting
        sort_by=request.query_params.get('sort_by',None)
        if sort_by:
            if sort_by == 'choices_asc':
                task=task.order_by('choices')
            elif sort_by == 'choices_desc':
                task=task.order_by('-choices')
        serializer=TaskSerializer(task,many=True)
        return Response(serializer.data)
    
    parser_classes = [MultiPartParser, FormParser] 

    def post(self, request):
        if 'file' in request.FILES:
            csv_file = request.FILES['file']
            
            if not csv_file.name.endswith('.csv'):
                return Response({"error": "File format not supported. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)
            
            data_set = csv_file.read().decode('UTF-8')
            io_string = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            csv_reader = csv.DictReader(io_string)
            
            tasks_created = []
            for row in csv_reader:
                try:
                    category = Category.objects.get(id=row['category'])
                    company = Company.objects.get(id=row['company'])

                    serializer = TaskSerializer(data=row)
                    if serializer.is_valid():
                        serializer.save(category=category, company=company)
                        tasks_created.append(serializer.data)
                    else:
                        return Response({"error": f"Error processing row: {row}", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
                except Category.DoesNotExist:
                    return Response({"error": f"Category not found: {row['category']}"}, status=status.HTTP_404_NOT_FOUND)
                except Company.DoesNotExist:
                    return Response({"error": f"Company not found: {row['company']}"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({"message": "Tasks created successfully", "tasks": tasks_created}, status=status.HTTP_201_CREATED)
        
        data = request.data
        try:
            category_id = Category.objects.get(id=data['category'])
            company_id = Company.objects.get(id=data['company'])
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(category=category_id, company=company_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)      
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Task Retrieve Update Delete View
class TaskRetrieveUpdateDeleteView(APIView):
    
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticatedOrReadOnly()]
        elif self.request.method=='PATCH' or self.request.method=='DELETE':
            return [IsAdminOrManager]
        return super().get_permissions()
        
    def get(self,request,pk):
        task=Task.objects.get(pk=pk)
        serializer=TaskSerializer(task)
        return Response(serializer.data)
    
    def patch(self,request,pk):
        task=Task.objects.get(pk=pk)
        serializer=TaskSerializer(task,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def delete(self,request,pk):
        task=Task.objects.get(pk=pk)
        task.delete()
        return Response({'Massage':'Delete SuccessFully'})

#Task Assign Get Create View
class TaskAssignGetCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.role in ['Admin', 'Manager']:
            taskassignments = TaskAssignment.objects.filter(company=user.company)
        else:
            taskassignments = TaskAssignment.objects.filter(user=user,company=user.company)
        serializer = TaskAssignSerializer(taskassignments, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        if user.role not in ['Admin', 'Manager']:
            return Response({"error": "You are not authorized to assign tasks."}, status=status.HTTP_403_FORBIDDEN)
        
        task_id = request.data.get('task')
        company_id = request.data.get('company')
        assigned_id = request.data.get('user')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        task = Task.objects.get(id=task_id)
        company = Company.objects.get(id=company_id)
        assign = User.objects.get(id=assigned_id)

        if assign.role != 'Employee':
            return Response({"error": "Tasks can only be assigned to Employees."}, status=status.HTTP_400_BAD_REQUEST)
        
        task_assignment, created = TaskAssignment.objects.get_or_create(
            task=task, 
            company=company, 
            user=assign,
            start_date=start_date,
            end_date=end_date
        )
        serializer = TaskAssignSerializer(task_assignment)
        
        send_mail(
            subject='Task assign confirmation',
            message=f'Task assigned  please complete before deadline',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Task Assign Retrieve Update Delete View
class TaskAssignRetrieveUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        try:
            taskassignment = TaskAssignment.objects.get(pk=pk)
            if user.role not in ['Admin', 'Manager'] and taskassignment.user != user:
                return Response({"error": "You are not authorized to view this task."}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskAssignSerializer(taskassignment)
            return Response(serializer.data)
        except TaskAssignment.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        user = request.user
        try:
            taskassignment = TaskAssignment.objects.get(pk=pk)
            if user.role not in ['Admin', 'Manager']:
                return Response({"error": "You are not authorized to update this task."}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskAssignSerializer(taskassignment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        except TaskAssignment.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        user = request.user
        try:
            taskassignment = TaskAssignment.objects.get(pk=pk)
            if user.role not in ['Admin', 'Manager']:
                return Response({"error": "You are not authorized to delete this task."}, status=status.HTTP_403_FORBIDDEN)

            taskassignment.delete()
            return Response({'message': 'Deleted successfully.'})
        except TaskAssignment.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
  
# Send Task Reminders View      
class SendTaskRemindersView(APIView):
    def post(self, request, format=None):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        overdue_tasks = TaskAssignment.objects.filter(end_date=tomorrow, status='pending')

        for task in overdue_tasks:
            send_mail(
                subject='Task Reminder',
                message=f'Your task "{task.task.name}" is not completed.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

        today = timezone.now().date()
        overdue_tasks = TaskAssignment.objects.filter(end_date__lt=today, status='pending')

        for task in overdue_tasks:
            send_mail(
                subject='Overdue Task',
                message=f'Your task "{task.task.name}" is overdue.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
        serializer=TaskAssignSerializer(overdue_tasks)

        return Response({"status": "Task reminders and overdue notifications sent"}, status=status.HTTP_200_OK)

# class Command(BaseCommand):
#     help = 'Send task reminders and overdue notifications'

#     def handle(self, *args, **kwargs):
#         tomorrow = timezone.now().date() + timezone.timedelta(days=1)
#         overdue_tasks = TaskAssignment.objects.filter(end_date=tomorrow, status='pending')

#         for task in overdue_tasks:
#             send_mail(
#                 'Task Reminder',
#                 f'Your task "{task.task.name}" is due tomorrow.',
#                 'dattatri34@gmail.com',
#                 [task.user.email],
#                 fail_silently=False,
#             )

#         today = timezone.now().date()
#         overdue_tasks = TaskAssignment.objects.filter(end_date__lt=today, status='pending')

#         for task in overdue_tasks:
#             send_mail(
#                 'Overdue Task',
#                 f'Your task "{task.task.name}" is overdue.',
#                 'dattatri34@gmail.com',
#                 [task.user.email],
#                 fail_silently=False,
#             )

