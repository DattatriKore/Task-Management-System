from django.urls import path
from .views import CategoriesGetCreateView,CategoriesRetrieveUpdateDeleteView,TaskGetCreateView,TaskRetrieveUpdateDeleteView,TaskAssignGetCreateView,TaskAssignRetrieveUpdateDeleteView,SendTaskRemindersView

urlpatterns=[
    path('category/',CategoriesGetCreateView.as_view()),
    path('category/<int:pk>/',CategoriesRetrieveUpdateDeleteView.as_view()),
    path('task/',TaskGetCreateView.as_view()),
    path('task/<int:pk>/',TaskRetrieveUpdateDeleteView.as_view()),
    path('taskassign/',TaskAssignGetCreateView.as_view()),
    path('taskassign/<int:pk>/',TaskAssignRetrieveUpdateDeleteView.as_view()),
    path('sendtaskreminders/',SendTaskRemindersView.as_view()),
]