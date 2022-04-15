from django.urls import path
from . import views

urlpatterns = [
    path('evaluation', views.evaluation, name='management-evaluation'),
    path('authorize_stripe', views.stripeAuthorizeView,
         name='management-authorize-stripe'),
    path('users/oauth/callback/', views.stripeAuthorizeCallbackView,
         name='management-authorize-callback'),
    path('job_offer/(P<uidb64>[0-9A-Za-z_\-]+)/(P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         views.managerOfferConfirmEmail, name='management-job-offer'),
    path('job_offer_page/<str:job_id>/', views.managerOfferConfirmPage,
         name='management-job-offer-page'),

]
