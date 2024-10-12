from django.urls import path
from .views import CompanyGetCreateView,CompanyRetrieveUpdateDeleteView

urlpatterns=[
    path('company/',CompanyGetCreateView.as_view()),
    path('company/<int:pk>/',CompanyRetrieveUpdateDeleteView.as_view()),
]
