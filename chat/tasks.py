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
def email_on_message(job_id, author, message):
    # Trying to send email
    try:
        print("Trying to send email")
        # Getting job id
        job_id = str(job_id)[5:]
        print(job_id)

        # Getting job
        current_job = JobPost.objects.get(job_id=job_id)
        
        # Getting manager
        client = current_job.client.username
        manager = current_job.manager.username
        if client == author:
            email = current_job.manager.email
            print("hahaahahahahhah")
        elif manager == author:
            email = current_job.client.email
            print("jiobeghje9rtiuhiwrtubgyrbehig")
        
        # Creating subject and body
        subject = "New Message from " + author
        body = message + "\nThis is a new message from " + author

        # Sending email
        email = EmailMessage(
            subject, body, to=[f'{email}'])
        print(email)
        email.send()
        print({email})

        return None
    except Exception as e:
        print("Failed to send email")
        print(e)
        return None
