# Importing celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task

# Importing profile and jobpost manager for management assignment
from users.models import Profile
from .models import JobPost, Milestone

# Importing email
from django.core.mail import EmailMessage

# Importing random for manager selection
import random

# Importing user model
from django.contrib.auth.models import User

# Importing manager job email func
from management.views import emailJobOffer

# Importing revoke to end future functions
from celery.task.control import revoke

# Creating manager assignement function
@periodic_task(run_every=(crontab(minute='*/20')), ignore_result=True)
def manager_assignment():

    # Getting unassigned jobs
    unassigned_jobs = JobPost.objects.filter(manager=None)
    print("unassigned_jobs")
    print(unassigned_jobs)

    if not unassigned_jobs:
        print('ha')

    # Looping through all the jobs
    for job in unassigned_jobs:
        print('job')
        print(job)

        client_name = job.client
        print("client_name")
        print(client_name)
        client = User.objects.get(username=client_name)

        # Getting capable managers with filter
        managers = Profile.objects.filter(
            is_manager=True, language=client.profile.language)
        print("Yo: ", managers)

        if managers:

            # Getting specific job
            current_job = JobPost.objects.get(pk=job.id)

            # Creating var to store
            selected_manager = None

            print('manager: ', managers)

            # Looping through managers
            for manager in managers:

                # Checking if user already received an application
                job_offers = current_job.job_offers

                # Spliting string into array of usernames
                job_offers_array = job_offers.split(',')

                # Randomly selecting managers
                manager_name = random.choice(managers)

               # Checking if user has stripe connected
                if not manager_name.stripe_user_id:
                    print('next option')
                    continue

                print(manager_name)
                print(job_offers)
                print(job_offers_array)

                # Looping through if job offer already sent
                if str(manager_name) in job_offers_array:
                    print('sent already')
                    continue

                # Getting manager user
                manager = User.objects.get(username=manager_name)

                # Assigning manager
                selected_manager = manager

                job_offer = job_offers + ',' + str(manager_name)

                current_job.job_offers = job_offer
                current_job.save()

                # Ending loop
                break

            print('selected_manager: ', selected_manager)

            # Checking if manager was selected
            if selected_manager:

                # getting current site and passing in to func

                # Emailing manager about job
                current_site = 'django-connect.herokuapp.com'
                emailJobOffer(selected_manager, job, current_site)
                print('aaa')
            else:
                print('manager not found')

    # Returning none
    return None

# Creating main milestone email task
@shared_task
def milestone_send_emails(pk, milestoneState, warning):
    try:
        job_obj = JobPost.objects.get(pk=pk)
        print('sdsffafdvefge')

        # Checking if job is none else returning
        if not job_obj:
            print("rgewrtgertg")
            revoke('service.tasks.milestone_send_emails')
            return None

        print("\n\n\n\nergwetrgewrtg")

        # Checking if specific milestone is active
        current_milestone = Milestone.objects.get(
            job=job_obj, milestone_number=milestoneState)
        print("current_milestone")
        print(current_milestone)
        # print(bool(current_milestone.active))
        # print(current_milestone)
        # if bool(current_milestone.active) == False or current_milestone == 'False':
        #     print('Testttstst')
        #     revoke('service.tasks.milestone_send_emails')
        #     return None

    except Exception as e:
        print(e)
        revoke('service.tasks.milestone_send_emails')
        return None
    print('milestones')

    if warning == False:
        # Sending email to client
        check_milestone_client_email(job_obj, milestoneState)

    # Sending email to manager
    milestone_manger_email(job_obj, milestoneState, warning)
    return None


# Alert milestone email clients
def check_milestone_client_email(job_obj, milestone):

    # Check if job still exist if not returning
    try:

        # Getting client and manager for email
        manager = job_obj.manager
        manager = User.objects.get(username=manager)
        manager = manager.username
        client = job_obj.client

        # Getting client emails
        client = User.objects.get(username=client)
        client_email = client.email
        client = client.username

        # Creating str variables
        if milestone == 1:
            milestone = 'One'
            body = 'Hello ' + client + ', We hope all is well, go to iblinkco.com to see rate ' + \
                manager + ' job so far? Make sure to let us know by contacting us at iblinkcompany@gmail.com'

        elif milestone == 2:
            milestone = 'Two'
            body = 'Hey ' + client + ', your manager, ' + manager + \
                ' second milestone is has been updated. Go to iblinkco.com to see it. If you have any questions email us at iblinkcompany@gmail.com. '

        elif milestone == 3:
            milestone = 'Three'
            body = 'Hello ' + client + ', you are more than halfway done with your job with, ' + manager + \
                ' and they have just updated their third milestone. Be sure to email us at iblinkcompany@gmail.com to update us on any problems you are having. '

        elif milestone == 4:
            milestone = 'Four'
            body = 'Hello ' + client + ', your job with, ' + manager + \
                ' has been completed. Make sure to long into your iBlinkco account now to see the work they have done and to give your final rating on their job.  '

        # Sending emails
        if job_obj.length == 3:
            if milestone == 3:
                milestone = 'Third'
                body = 'Hello ' + client + ', your job with, ' + manager + \
                    ' has been completed. Make sure to long into your iBlinkco account now to see the work they have done and to give your final rating on their job.  '
        # Client email
        email = EmailMessage(
            'Milestone ' + milestone + ' Check In and Rate', body, to=[f'{client_email}'])
        print(email)
        email.send()
        print({email})

        return None
    except Exception as e:
        print("eeeeeee")
        print(e)
        return None

# Alert milestone email managers


def milestone_manger_email(job_obj, milestoneState, warning):
    print('dfdfdfdfdf')

    # Checking if we can retrieve job else returning
    try:
        # Getting client and manager for email
        manager = job_obj.manager

        client = job_obj.client
        client = User.objects.get(username=client)
        client = str(client.username)

        # Getting client emails
        manager_email = User.objects.get(username=manager)
        manager = str(manager.username)
        print(manager_email)
        manager_email = str(manager_email.email)
        print(manager_email)

        # Creating str variables
        if milestoneState == 1:

            # Checking if this is a warning email
            if warning == True:
                subject = 'Your First Milestone of your Job With ' + client + ' is Almost Due!'
                body = 'Hello ' + manager + ', We hope all is well, How is your job with ' + client + \
                    ' going so far? Make sure to update your first milestone by tomorrow. If you have any questions, contact us at iblinkcompany@gmail.com'

            # Sending due email
            else:
                subject = 'Your First Milestone is Due Today!'
                body = 'Hello ' + manager + ', We hope all is well, your first milestone with ' + client + \
                    ' is due today. If you have any questions let us know by contacting us at iblinkcompany@gmail.com'

        elif milestoneState == 2:
            if warning == True:

                subject = 'Your Second Milestone of your Job With ' + client + ' is Due Tomorrow!'
                body = 'Hi ' + manager + ', We hope all is well, you are currently working towards you second milestone of your job with ' + client + \
                    ' Do not forget to update the milestone on the website and if you have any questions let us know by contacting us at iblinkcompany@gmail.com'
            else:
                subject = 'Your Second Milestone of your Job With ' + client + ' is Due Tomorrow!'
                body = 'Hey ' + manager + ', your manager, ' + manager + \
                    ' second milestone is due. email us at iblinkcompany@gmail.com. '

        elif milestoneState == 3:
            if warning == True:
                subject = 'Your Third Milestone of your Job With ' + client + ' is Due Tomorrow!'
                body = 'Hello ' + manager + ', you are more than halfway done with your job with, ' + manager + \
                    '. Be sure to email us at iblinkcompany@gmail.com to update us on any problems you are having. '
            else:
                subject = 'Your Third Milestone of your Job With ' + client + ' is Due Today!'
                body = 'Hey ' + manager + ', your third milestone of your job with , ' + manager + \
                    ' is due. Be sure to email us at iblinkcompany@gmail.com to update us on any problems you are having. '

        elif milestoneState == 4:
            if warning == True:
                subject = 'Your Fourth and Final Milestone of your Job With ' + \
                    client + ' is Due Tomorrow!'
                body = 'Hello ' + manager + ', you are more than halfway done with your job with, ' + manager + \
                    '. Be sure to email us at iblinkcompany@gmail.com to update us on any problems you are having. '
            else:
                subject = 'Your last milestone with ' + client + ' is due'
                body = 'Hello ' + manager + ', your job with, ' + manager + \
                    ' will be completed today. Make sure to long into your iBlinkco account to finish your fourth milestone if you have not. '

        if job_obj.length == 3:
            if milestoneState == 3:
                if warning == True:
                    subject = 'Your Third and Final Milestone of your Job With ' + \
                        client + ' is Due Tomorrow!'
                    body = 'Hello ' + manager + ', you are more than halfway done with your job with, ' + manager + \
                        '. Be sure to email us at iblinkcompany@gmail.com to update us on any problems you are having. '
                else:
                    subject = 'Your last milestone with ' + client + ' is due today'
                    body = 'Hello ' + manager + ', your job with, ' + manager + \
                        ' will be completed today. Make sure to long into your iBlinkco account to finish your third milestone if you have not. '

       # Sending emails
        email = EmailMessage(
            subject, body, to=[f'{manager_email}'])
        print(email)
        email.send()
        print({email})

    except Exception as e:
        print(e)


# Task to send rate job email
@shared_task
def rateJobEmail(manager, client, client_email):

    subject = "Rate" + manager + "'s job now"
    body = "Hello " + client + ", your job with " + manager + \
        " is complete. Rate there job here and let us know how your experience with iBlinkco is going be emailing us at iblinkcompany@gmail.com "

    # Sending emails
    email = EmailMessage(
        subject, body, to=[f'{client_email}'])
    print(email)
    email.send()

    print({email})

# Task to notify manager about milestone being rated
@shared_task
def milestoneRatedEmail(manager, client, manager_email, milestone_number, star_count):

    # Checking what number
    if milestone_number == 1:
        milestone_number = 'one'
    elif milestone_number == 2:
        milestone_number = 'two'
    elif milestone_number == 3:
        milestone_number = 'three'
    elif milestone_number == 4:
        milestone_number = 'four'

    subject = client + " has rated your job during milestone " + \
        str(milestone_number) + " " + str(star_count) + " stars"

    if star_count == 5:
        greatness_of_job = " seems to be going great! They gave you " + \
            str(star_count) + " on your last milestone."
    elif star_count == 4:
        greatness_of_job = " seems to be going good. They gave you " + \
            str(star_count) + \
            " on your last milestone which means they like the job but maybe you can do better."
    elif star_count == 3:
        greatness_of_job = " is tolerable. They gave you " + \
            str(star_count) + " on your last milestone. We encourage you step up for the next milestone to avoid having your overall rating significantly penalized."
    elif star_count < 3:
        greatness_of_job = " wasn't as good as they expected. They gave you " + \
            str(star_count) + " on your last milestone. We encourage you step up for the next milestone to avoid having your overall rating significantly penalized. Too many low stars on your accounts can get your account disabled."

    ending = " If you have any questions or concerns email us at iblinkcompany@gmail.com"
    body = "Hello " + manager + ", your job with " + \
        client + greatness_of_job + ending

    # Sending emails
    email = EmailMessage(
        subject, body, to=[f'{manager_email}'])
    print(email)
    email.send()

    print({email})
    return 'success'


@shared_task
def jobPrepEndedEmail(manager, client, client_email):

    subject = 'Job preparation period ended. ' + \
        manager + ' will start working on your job.'
    body = "Hello " + client + ", " + manager + \
        " has ended their job preperation period and is starting to work on your requested services."

    # Sending email to client
    email = EmailMessage(
        subject, body, to=[f'{client_email}'])
    print(email)
    email.send()


@shared_task
def jobCancelledEmail(manager, client, client_email, manager_email):

    subject = f'Your cancelled your job with {manager}'
    body = f'Hello {client},\nYour job with {manager} has been cancelled. If you have any questions or concerns please respond to this email.'

    # Sending email to client
    email = EmailMessage(subject, body, to=[f'{client_email}'])
    print(email)
    email.send()

    subject = f'Your client {client} cancelled the job'
    body = f'Hello {manager},\nYour job with {client} has been cancelled. If you have any questions or concerns please respond to this email.'

    # Sending email to manager
    email = EmailMessage(subject, body, to=[f'{manager_email}'])
    print(email)
    email.send()


# manager_assignment()
