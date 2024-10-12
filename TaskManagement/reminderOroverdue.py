from celery import shared_task
from .models import TaskAssignment
from django.core.mail import send_mail

@shared_task
def send_task_reminder(task_assignment_id):
    task_assignment = TaskAssignment.objects.get(id=task_assignment_id)
    user_email = task_assignment.user.email
    subject = 'Task Reminder'
    message = f'Reminder: Your task "{task_assignment.task.title}" is due tomorrow.'
    
    send_mail(subject, message, 'from@example.com', [user_email])

@shared_task
def send_overdue_notification(task_assignment_id):
    task_assignment = TaskAssignment.objects.get(id=task_assignment_id)
    user_email = task_assignment.user.email
    subject = 'Overdue Task Notification'
    message = f'Your task "{task_assignment.task.title}" is overdue.'
    
    send_mail(subject, message, 'from@example.com', [user_email])

#celery -A your_project_name worker --loglevel=info