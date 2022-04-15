# Importing celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task

# Importing profile and user objects
from users.models import Profile
from django.contrib.auth.models import User
from management.models import ManagerEvaluation

# Importing email
from django.core.mail import EmailMessage

# User email func one day after account creation
@shared_task
def userCreationOneDayCheckin(user_id):

    # Trying to get user and platform
    try:
        user = User.objects.get(user_id)
        profile = Profile.objects.get(user)
    except Exception as e:
        return None

    # Checking if user is user has selected user type
    if profile.is_manager == False and profile.is_client == False:
        print('user yet to choose profile type')
        subject = 'Select your account type now!.'
        body = f"Hello {user.username},\nwe are happy you created an account on iblinkco.com. You have yet to choose if you are a client looking for social media services or a qualified manager who is interested in providing social media services."
    # Checking if user is a manager
    elif profile.is_manager == True:
        print('sdsds')
        evaluation = ManagerEvaluation.objects.get(user)
        if evaluation.evaluation_completed == False:
            subject = 'Finish your Manager Evaluation'
            body = f"Hello {user.username},\nPlease finish your evaluation if you are still interested in providing social media management services to business through our platform."
    # Checking if user is a client
    # elif profile.is_client == True:
    #     subject = 'Post a Job Now!'
    #     body = f"Hello {user.username},\nwe are happy you signed up on iblinkco.com. Post your first job now to be assigned with a qualified manager to help you grow and stay consistent on social media management."

    # Sending email to client
    email = EmailMessage(
        subject, body, to=[f'{user.email}'])
    print(email)
    email.send()
    return None
