# from apscheduler.schedulers.blocking import BlockingScheduler

# # Importing email
# from django.core.mail import EmailMessage

# sched = BlockingScheduler()


# @sched.scheduled_job('interval', minutes=3)
# def timed_job():
#     subject = "test"
#     body = "please work!"
#     client_email = "iblinkcompany@gmail.com"
#     email = EmailMessage(subject, body, to=[f'{client_email}'])
#     print(email)
#     email.send()
#     print('This job is run every three minutes.')


# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')


# sched.start()
