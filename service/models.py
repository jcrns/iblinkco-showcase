from django.db import models

# Importing to configure before save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from .choices import * 

# Importing to create job id
from webapp.utils import random_string_generator

from users.models import Profile

# Importing email
from django.core.mail import EmailMessage

# Import stripe
import stripe

# import django.contrib.postgres.fields import ArrayField

from datetime import timedelta, datetime
import pytz 
class JobPost(models.Model):

    # JOB ID
    job_id = models.CharField(max_length=120, blank=True)
    
    # Users involved
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client', null=True)
    manager = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='manager', blank=True)
    
    # Will be set to false when job ends or is cancelled
    active = models.BooleanField(default=True)

    # Job Length
    number_of_post = models.IntegerField()
    length = models.IntegerField()
    
    # Paying
    manager_payment = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    price_paid = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    paid_for = models.BooleanField(default=False)
    job_fee = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    manager_paid = models.BooleanField(default=False)

    # Job Details

    # Defining job complete bool and original job 
    job_complete = models.BooleanField(default=False)
    job_rating = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    captions = models.BooleanField(default=False)
    search_for_content = models.BooleanField(default=False)
    post_for_you = models.BooleanField(default=False)
    engagement = models.BooleanField(default=False)
    service_description = models.CharField(max_length=5000, default='none')
    manager_randomly_assigned = models.BooleanField(default=True)
    auto_renewal = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    # Platforms
    instagram = models.BooleanField(default=False)
    facebook = models.BooleanField(default=False)

    # Platform Username
    instagram_username = models.CharField(max_length=100, blank=True, default='none')
    facebook_username = models.CharField(max_length=100, blank=True, default='none')

    # Job Preparation
    job_preparation_completed = models.BooleanField(default=False)
    job_preparation_deadline = models.DateTimeField(
        max_length=8, blank=True, null=True)

    # Date Job Posted
    date_requested = models.DateTimeField(
        verbose_name='date requested', auto_now_add=True)

    # Deadline for job
    deadline = models.DateTimeField(max_length=8, blank=True, null=True)
    
    # Client job rating
    # How was your experience with {client}?
    client_job_rating = models.IntegerField(default=0, blank=True)

    job_offers = models.CharField(max_length=5000, blank=True, default='none')

    def __str__(self):
        print(self.manager)
        return f'{self.client} Job Request {self.job_id}'

    # Overriding the save function to check if manager was assigned
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        
        # Checking if user job is complete
        print("self.job_complete")
        print(self)
        print(self.job_complete)
        if self.job_complete == True:

            # Checking if active is True if so setting to False
            if self.active == False:
                self.active = True

            print("self.manager_paid")

            # Getting users involved
            client = Profile.objects.get(user=self.client)
            manager = Profile.objects.get(user=self.manager)

            # Checking if client is busy if so changing bool false
            print("client.profile.busy")
            print(client.busy)
            if client.busy == True:
                client.busy = False
                print(client.busy)
                client.save()
            print("self.manager_paid")
            print(self.manager_paid)

            # Checking if manager is paid
            if self.manager_paid == False:
                
                # Getting manager data
                stripe_id = manager.stripe_user_id

                # Calculating payment in pennies
                manager_payment = int(self.manager_payment*100)
                print('asasas')

                
                # Paying managers with stripe
                stripe.Transfer.create(
                    amount=manager_payment,
                    currency="usd",
                    destination=stripe_id,
                )
                
                self.manager_paid = True

                # Emailing client to rate job
                client = User.objects.get(username=client)
                client_email = client.email
                
                manager = self.manager.username
                client = self.client.username

                # Getting client email
                rateJobEmail(manager, client, client_email)


        super(JobPost, self).save(force_insert, force_update, *args, **kwargs)


# Checking if acceptance has changed
def manager_previously_existed_check(sender, instance, **kwargs):
    print('sfsdsdsdsdsds')
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field hasn't technically changed, but you may want to do something else here.
        obj = None
        pass
    
    if obj is not None:
        # Checking if manager used to be null
        if not obj.manager == instance.manager:
                
            # Creating deadline for job
            now = datetime.now(pytz.utc)

            print('current time', now)
            print(obj.manager)
            print(instance.manager)
            print("instance.manager")
            # Getting absolute job length by adding regular job length and preparation time
            realJobLength = instance.length + 2

            # Adding the absolute job length to current time
            deadline = now + timedelta(days=realJobLength)
            print('new deadline', deadline)
            instance.deadline = deadline

            # Getting preparation time
            now = now + timedelta(days=2)
            instance.job_preparation_deadline = now
            
            # Trying to send email
            try:
                # Preparing for email by getting vars
                client = instance.client
                client = User.objects.get(username=client)
                manager = instance.manager
                manager = User.objects.get(username=manager)

                # Defining emails vars
                client_email = client.email
                manager_email = manager.email
                
                # Getting users usernames
                manager = instance.manager.username
                client = instance.client.username

                # Sending email to client
                managerAssignedEmails(
                    manager, client, client_email, manager_email)
            except Exception as e:
                print(e)

            # Schedule job prep deadline email

def pre_save_create_job_id(sender, instance, *args, **kwargs):
    if not instance.job_id:
        instance.job_id = random_string_generator(size=16)


pre_save.connect(manager_previously_existed_check, sender=JobPost)
pre_save.connect(pre_save_create_job_id, sender=JobPost)


def managerAssignedEmails(manager, client, client_email, manager_email):

    subject = "Congrats your job request has been assigned to " + manager
    body = "Hello " + client + ", your latest job request now has an assignment! The job will start with a 2 day prep period for the manager. Thank you! If you have any further question or concerns email us at iblinkcompany@gmail.com "

    # Sending emails
    email = EmailMessage(
        subject, body, to=[f'{client_email}'])
    print(email)
    email.send()

    print({email})

    subject = "Congrats you have been assigned to work with " + client + " on their latest job request"
    body = "Hello " + manager + ", you have been assigned to work with " + client + \
        " on their latest job request! The job will start with a 2 day prep period for the manager. Thank you! If you have any further question or concerns email us at iblinkcompany@gmail.com "

    # Sending emails
    email = EmailMessage(
        subject, body, to=[f'{manager_email}'])
    print(email)
    email.send()

    print({email})


def rateJobEmail(manager, client, client_email):

    subject = "Rate " + manager + "'s job now"
    body = "Hello " + client + ", your job with " + manager + " is complete. Rate there job here and let us know how your experience with iBlinkco is going be emailing us at iblinkcompany@gmail.com "

    # Sending emails
    email = EmailMessage(
        subject, body, to=[f'{client_email}'])
    print(email)
    email.send()

    print({email})

# Milestone models
class Milestone(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    milestone_number = models.IntegerField(default=0)
    milestone_rating = models.IntegerField(default=0)
    milestone_statement = models.CharField(
        max_length=1000, default='none')
    milestone_post_goal_completed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    deadline = models.DateTimeField(max_length=8, blank=True, null=True)

    def __str__(self):
        return f'{self.milestone_number} Milestone for {self.job}'

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # Checking if deadline is null
        if not self.deadline:
            # Setting new deadline by checking for specific job length
            if self.job.length == 14:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=3)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=7)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=10)
                elif self.milestone_number == 4:
                    milestoneTimeDays = timedelta(days=14)

            elif self.job.length == 10:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=2)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=4)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=7)
                elif self.milestone_number == 4:
                    milestoneTimeDays = timedelta(days=10)

            elif self.job.length == 10:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=2)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=4)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=7)
                elif self.milestone_number == 4:
                    milestoneTimeDays = timedelta(days=10)

            elif self.job.length == 7:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=2)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=3)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=5)
                elif self.milestone_number == 4:
                    milestoneTimeDays = timedelta(days=7)

            elif self.job.length == 5:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=2)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=3)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=4)
                elif self.milestone_number == 4:
                    milestoneTimeDays = timedelta(days=5)

            elif self.job.length == 3:
                if self.milestone_number == 1:
                    milestoneTimeDays = timedelta(days=2)
                elif self.milestone_number == 2:
                    milestoneTimeDays = timedelta(days=3)
                elif self.milestone_number == 3:
                    milestoneTimeDays = timedelta(days=4)
            now = datetime.now()
            deadline = now + milestoneTimeDays
            self.deadline = deadline
        super(Milestone, self).save(
            force_insert, force_update, *args, **kwargs)

# Milestone file model
class MilestoneFiles(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    milestoneOne = models.BooleanField(default=False)
    milestoneTwo = models.BooleanField(default=False)
    milestoneThree = models.BooleanField(default=False)
    milestoneFour = models.BooleanField(default=False)
    milestoneFile = models.FileField()
