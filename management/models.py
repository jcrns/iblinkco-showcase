from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django_resized import ResizedImageField
from django.core.mail import EmailMessage
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ManagerPreference(models.Model):
    # Manager
    manager = models.OneToOneField(User, on_delete=models.CASCADE)

    # Preferences
    business_list_order = models.CharField(max_length=500, default='none')
    length = models.IntegerField(default=0)
    post_per_day = models.IntegerField(default=0)
    instagram = models.BooleanField(default=False)
    facebook = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.manager} Preferences'

# class ManagerBiases(models.Model):
#     # Manager
#     manager = models.OneToOneField(User, on_delete=models.CASCADE)

#     # Preferences
#     business_list_order = models.CharField(max_length=500, default='none')
#     # length = models.IntegerField(default=0)
#     # post_per_day = models.IntegerField(default=0)
#     instagram = models.BooleanField(default=False)
#     facebook = models.BooleanField(default=False)
#     completed = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.manager} Preferences'

class ManagerEvaluation(models.Model):
    # Manager
    manager = models.OneToOneField(User, on_delete=models.CASCADE)

    # Checking if evaluation was started 
    evaluation_started = models.BooleanField(default=False)
    
    # Checking if manager was accepted or declined and creating prevalue to see if it is changed
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)

    # Checking if evaluation was completed
    evaluation_completed = models.BooleanField(default=False)

    # Question one answer 
    answer_one_caption_one = models.TextField(max_length=2200, default='none')
    answer_one_caption_two = models.TextField(max_length=2200, default='none')
    answer_one_caption_three = models.TextField(max_length=2200, default='none')
    
    # sample answer
    # 1. ....
    # 2 ...

    # Question two answer 
    answer_two_caption = models.TextField(max_length=2200, default='none')
    answer_two_what_are_problems = models.TextField(max_length=2200, default='none')
    answer_two_img = models.ImageField(default='default.jpg', upload_to='application_pics')

    # Question three answer
    answer_three_caption = models.TextField(max_length=2200, default='none')
    answer_three_img = models.ImageField(default='default.jpg', upload_to='application_pics')

    # Question four answer
    choose_job = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.manager} Evaluation'
    
    # Overriding the save func to change certain attr
    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        # Checking if job is accepted
        if self.accepted == True:
            # Checking if evaluation is completed else changing it to compelted
            if self.evaluation_completed == False:
                self.evaluation_completed = True
        super(ManagerEvaluation, self).save(
            force_insert, force_update, *args, **kwargs)


    # Email manager accepted
    def managerAcceptanceEmail(self, acceptance):
        user = self.manager

        if acceptance == True:
            # Creating subject
            mail_subject = 'Congratulations ' + user.username + \
                ' You Have Been Verified for iBlinkco'

            # Creating message body and rendering from template
            messageBody = 'You are now able to conduct social media management services for clients on iblinkco.com. Be sure to consistently check your email as we will let you know when you have been assigned to a job.'
        else:
            # Creating subject
            mail_subject = "We are sorry to inform you that you didn't pass the verification"
            messageBody = "Sorry but you didn't pass iBlinkco's social media management evaluation. You would be allowed to take another in 1 month. If you have any further questions email us at iblinkcompany@gmail.com"
        # Getting email
        email = user.email

        print(email)

        # Sending email
        email = EmailMessage(mail_subject, messageBody, to=[f'{email}'])
        # email.send()
        return email

    def managerDeclined(self):
        user = self.manager
        # Getting current site
        mail_subject = "We are sorry to inform you that you didn't pass the verification"

        # Creating message body and rendering from template
        messageBody = "Sorry but you didn't pass iBlinkco's social media management evaluation. You would be allowed to take another in 1 month. If you have any further questions email us at iblinkcompany@gmail.com"

        # Getting email
        email = user.email

        print(email)

        # Sending email
        email = EmailMessage(mail_subject, messageBody, to=[f'{email}'])
        email.send()
        return email

# Checking if acceptance has changed
@receiver(pre_save, sender=ManagerEvaluation)
def manager_acceptance(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field hasn't technically changed, but you may want to do something else here.
        pass
    else:
        # Checking if user has been accepted
        if not obj.accepted == instance.accepted:
            if instance.accepted == True:
                # Sending Email if user was accepted
                ManagerEvaluation.managerAcceptanceEmail(instance, True)

        elif not obj.declined == instance.declined:
            if instance.declined == True:
                # Sending Email if user was declined
                ManagerEvaluation.managerAcceptanceEmail(instance, False)
