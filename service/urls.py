from django.urls import path
from . import views

urlpatterns = [
    path('post_a_job_select', views.postJobSelect, name='service-job-select'),
    path('post_a_job', views.postJob, name='service-job'),
    path('complete_profile_client', views.completeProfileClient, name='service-complete-profile-client'),
    path('complete_profile_manager', views.completeProfileManager, name='service-complete-profile-manager'),
    path('checkout/<str:job_id>', views.checkoutHome, name='service-checkout'),
    path('charge/<str:job_id>', views.charge, name='service-charge'),
    path('job-renewal/<str:job_id>', views.jobRenewal,
         name='service-job-renewal-request'),
    path('test-transaction/<str:job_id>', views.testTransaction,
         name='service-test-transaction'),
    path('job_success/<str:job_id>', views.jobPaymentSuccess,
         name='service-job-success'),
]
