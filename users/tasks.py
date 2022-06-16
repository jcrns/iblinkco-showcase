# Importing celery
# from celery.schedules import crontab
# from celery.decorators import periodic_task
# from celery.task.control import revoke
# from celery import shared_task
from datetime import *
import json
from webapp.celery import app


# Importing profile and user objects
from users.models import Profile
from django.contrib.auth.models import User
from management.models import ManagerEvaluation

# Importing email
from django.core.mail import EmailMessage

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

# chon_schedule = CrontabSchedule.objects.create(minute='0', hour='18') # To create a cron schedule. 
# schedule = IntervalSchedule.objects.create(every=10, period=IntervalSchedule.SECONDS) # To create a schedule to run everu 10 min.
# PeriodicTask.objects.create(crontab=chon_schedule, name='name_to_identify_task',task='name_of_task') # It creates a entry in the database describing that periodic task (With cron schedule).
# task = PeriodicTask.objects.create(interval=schedule, name='run for every 10 min', task='for_each_ten_min', ) # It creates a periodic task with interval schedule


# @app.task(name='users.test_email')
# def testEmail():
#     subject = 'Finish your Manager Evaluation'
#     body = f"Hello User,\nPlease finish your evaluation if yo=u are still interested in providing social media management services to business through our platform."
#     email='jaydencummings1000@gmail.com'
    
#     # Checking if user is a client
#     email = EmailMessage(
#     subject, body, to=[f'{email}'])
#     print(email)
#     email.send()

# User email func one day after account creation
@app.task(name='users.follow_up_email')
def sendUserEmail(subject, body, userEmail, uid):
    taskName="user_follow_up_email_"
    try:
        # Sending email to client
        email = EmailMessage(
            subject, body, to=[f'{userEmail}'])
        print(email)
        email.send()
    except Exception as e:
        print(e)
        print("email not sent")

    print("deleting obk")

    # Deleting Task out of database
    PeriodicTask.objects.filter(name=taskName+uid).delete()

    return None

def userCreationOneDayCheckin(user_id):

    taskName="user_follow_up_email_"
    print("Start")
    print(user_id)
    # Trying to get user and platform
    try:
        user = User.objects.filter(pk=user_id).first()
        print("user")
        print(user)

        profile = Profile.objects.filter(user=user).first()
        print("profile")
        print(profile)

        # Checking if user is user has selected user type
        if profile.is_manager == False and profile.is_client == False:
            print('user yet to choose profile type')
            subject = 'Welcome to iBlikco.com! Select your account type now!.'
            body = f"Hello {user.username},\nwe are happy you have created an account on iblinkco.com. You have yet to choose if you are a client looking for social media services or a qualified manager who is interested in providing social media services."
       
        # Checking if user is a manager
        elif profile.is_manager == True:
            print('sdsds')
            evaluation = ManagerEvaluation.objects.get(user)
            if evaluation.evaluation_completed == False:
                subject = 'Finish your Manager Evaluation'
                body = f"Hello {user.username},\nPlease finish your evaluation if yo=u are still interested in providing social media management services to business through our platform."
        # Checking if user is a client
        # elif profile.is_client == True:
        #     subject = 'Post a Job Now!'
        #     body = f"Hello {user.username},\nwe are happy you signed up on iblinkco.com. Post your first job now to be assigned with a qualified manager to help you grow and stay consistent on social media management."

        expiredTime = datetime.now() + timedelta(hours=1)
        schedule = IntervalSchedule.objects.create(every=20, period=IntervalSchedule.SECONDS) # To create a schedule to run everu 10 min.
        PeriodicTask.objects.create(
            interval=schedule, 
            name='user_follow_up_email_'+user_id, 
            task='users.follow_up_email', 
            one_off=True, 
            # args=json.dumps([uid,]), 
            kwargs=json.dumps({ 'subject': subject, 'body': body, 'userEmail': user.email, 'uid': user_id }),
            expires=expiredTime,
        ) # It creates a periodic task with interval schedule
        print("finished")

        
    except Exception as e:
        print(e)
        print("email not sent")

    print("complete")
