from rest_framework import serializers
from UserAuth.serializers import UserProfileSerializer
from CompanyManagement.serializers import CompanySerializer
from .models import Category,Task,TaskAssignment
from django.utils import timezone
from datetime import timedelta
from .reminderOroverdue import *

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name']
        
# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    category=CategorySerializer(read_only=True)
    class Meta:
        model=Task
        fields=['id','title','description','category','priority','company','created_at']
        
# Task Assign Serializer
class TaskAssignSerializer(serializers.ModelSerializer):
    task=TaskSerializer(read_only=True)
    company=CompanySerializer(read_only=True)
    user=UserProfileSerializer(read_only=True)
    class Meta:
        model=TaskAssignment
        fields=['id','task','company','user','start_date','end_date','status']
        
    def create(self,validated_data):
        user=self.context['request'].user
        role=user.role
        
        if role=='Admin' or role=='Manager':
            return super().create(validated_data)
        else:
            raise serializers.ValidationError('Only Admins and Manager can assign tasks.')

# class TaskAssignSerializer(serializers.ModelSerializer):
#     # ... (existing code)
    
#     def create(self, validated_data):
#         user = self.context['request'].user
#         role = user.role
        
#         if role == 'Admin' or role == 'Manager':
#             task_assignment = super().create(validated_data)

#             # Schedule reminder email for 1 day before end_date
#             if task_assignment.end_date:
#                 reminder_date = task_assignment.end_date - timedelta(days=1)
#                 if reminder_date > timezone.now().date():
#                     send_task_reminder.apply_async((task_assignment.id,), eta=reminder_date)

#             # Schedule overdue email for the end_date
#             if task_assignment.end_date:
#                 overdue_date = task_assignment.end_date
#                 send_overdue_notification.apply_async((task_assignment.id,), eta=overdue_date)

#             return task_assignment
#         else:
#             raise serializers.ValidationError('Only Admins and Managers can assign tasks.')
