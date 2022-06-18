from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard-home'),
    path('job-details-client/<int:pk>/', views.JobDetailView.as_view(template_name='dashboard/job_detail_client.html'), name='dashboard-job-detail-client'),
    path('job-details-manager/<int:pk>/', views.JobDetailView.as_view(template_name='dashboard/job_detail_manager.html'), name='dashboard-job-detail-manager'),
    path('confirm-job/<int:pk>/', views.ConfirmJobDetailView.as_view(), name='dashboard-confirm-job'),
    path('job-details/<int:pk>/delete/',
         views.deleteJob, name='dashboard-job-delete'),
    path('job-details/<int:pk>/end-job-prep/',
         views.jobPrepEnded, name='dashboard-end-job-prep'),
]
