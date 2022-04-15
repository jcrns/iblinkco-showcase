# Importing celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task

# Importing profile and jobpost manager for management assignment
from users.models import Profile
from service.models import JobPost

# Importing email
from django.core.mail import EmailMessage

# Importing random for manager selection
import random

# Importing user model
from django.contrib.auth.models import User

# Importing revoke to end future functions
from celery.task.control import revoke

# Manager job preperation ended email
@shared_task
def manager_job_preperation_email(pk):
    try:
        job_obj = JobPost.objects.get(pk=pk)
        print('job prep email')

        # Checking if job is none else returning
        if not job_obj:
            return None

        # Checking if job prep has started
        if job_obj.job_preparation_completed == True:
            print('returning func')
        else:
            print('sending job prep email')

        manager_name = str(job_obj.manager)
        client_name = str(job_obj.client)
        client_email = job_obj.client.email
        body = f"Hello {manager_name}, the preperation period for your job with {client_name} has ended. Go to the job details."
        # Client email
        email = EmailMessage(
            'Your Job Preperation has Ended!', body, to=[f'{client_email}'])
        print(email)
        email.send()
        print({email})
        return None

    except Exception as e:
        print(e)
        return None
