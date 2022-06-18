from django.db import models
from django.contrib.auth.models import User
from service.models import JobPost
from webapp.utils import random_string_generator
from django.db.models.signals import pre_save
from .tasks import email_on_message

class Message(models.Model):
    # job = models.ForeignKey(JobPost, on_delete=models.CASCADE )
    job = models.CharField(max_length=120, default='none')
    message_id = models.CharField(max_length=120, blank=True)
    author = models.ForeignKey(
        User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    recipient_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.author.username

    # Overriding the save function to check if manager was assigned
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        print("saving message")
        
        email_on_message.delay(self.job, str(self.author), self.content)
        super(Message, self).save(force_insert, force_update, *args, **kwargs)

    def last_10_messages(job_id,):

        # last_ten = Message.objects.filter(job=job_id).order_by('-timestamp')[:20]
        last_ten = Message.objects.filter(job=job_id).order_by('-timestamp')
        last_ten = reversed(last_ten)
        return last_ten

def pre_save_create_message_id(sender, instance, *args, **kwargs):
    if not instance.message_id:
        instance.message_id = random_string_generator(size=10)

pre_save.connect(pre_save_create_message_id, sender=Message)
