from django.shortcuts import render, redirect

# Lib to require login for certain views
from django.contrib.auth.decorators import login_required

# Adding mixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Importing list view to list past jobs
from django.views.generic import DetailView, DeleteView

# Importing lib to get specific objects
from django.shortcuts import get_object_or_404

# Importing db charfield to add fields to querysets
from django.db.models import CharField, Value

# Importing profile to access 
from users.models import Profile

# Importing jobs to access
from service.models import JobPost, MilestoneFiles, Milestone

# Importing user
from django.contrib.auth.models import User

# Importing job form for form updates in detail views
from service.forms import JobPostFormUpdate, milestoneUpdate

# Importing Complete Profile
from users.forms import ProfileUpdateFormClient, ProfileUpdateFormManager

# Getting user evaluation modal
from management.models import ManagerEvaluation

# Importing datetime
from datetime import datetime, timezone

from django.http import HttpResponse

# Importing stripe
import stripe

# Importing task
from service.tasks import milestoneRatedEmail, jobPrepEndedEmail, milestone_send_emails, jobCancelledEmail
from datetime import timedelta, datetime

# Importing chats
from chat.models import Message

# Overview function
@login_required(login_url="/?login=true")
def dashboard(request):
    # Getting user
    profile = request.user.profile
    if profile.is_client == False and profile.is_manager == False:
        return redirect('homepage-overview')
    
    # Checking if user is client or manager
    if profile.is_client == True:
        if profile.business_type != 'none':
            update_profile_form = ProfileUpdateFormClient(instance=request.user.profile)
            past_orders = JobPost.objects.filter(
                client=request.user.pk, job_complete=True, cancelled=False).order_by('-date_requested')
            currentJob = JobPost.objects.filter(client=request.user.pk, job_complete=False, cancelled=False)

            # Counting unread messages
            if currentJob:
                unread_client = number_of_unread_messages(currentJob[0].client, currentJob[0].job_id)
            else:
                unread_client = 0

            # Checking if request used post method
            if request.method == 'POST':
                
                # Creating update profile form with post data
                update_profile_form = ProfileUpdateFormClient(request.POST or None, request.FILES or None, instance=request.user.profile)
                
                # Checking if update profile form is valid
                if update_profile_form.is_valid():
                    profile = update_profile_form.save(commit=False)
                    profile.user = request.user
                    profile.save()
                    return redirect('dashboard-home')
            return render(request, 'dashboard/client.html', {'profile': profile, 'current_job': currentJob, 'past_orders': past_orders, 'update_profile_form': update_profile_form, "static_header": True, "nav_black_link": True, "unread_client": unread_client})
        else:
            return redirect('service-complete-profile-client')
    # If manager
    else:
        print("SDSDSD")
        # Checking if profile is completed
        if profile.description != 'none':

            # Getting evaluation
            evaluation = ManagerEvaluation.objects.get(manager=request.user)
            
            print("evaluation.accepted")
            print(evaluation.accepted)

            
            # Checking if evaluation is completed
            if evaluation.accepted == True:
                print('accepted')
            
                # Get jobs involved
                update_profile_form = ProfileUpdateFormManager(instance=request.user.profile)
                past_jobs = JobPost.objects.filter(
                    manager=request.user.pk, job_complete=True, cancelled=False).order_by('-date_requested')
                current_jobs = JobPost.objects.filter(
                    manager=request.user.pk, job_complete=False, cancelled=False).order_by('-date_requested')
                print('profile.stripe_user_id')
                
                # Adding number of unread messages to jobs
                for job in current_jobs:
                    # Getting number of unread messages
                    unread_messages = number_of_unread_messages(job.manager, job.job_id)
                    job.unread_messages = unread_messages
                
                # Getting job opportunities by getting jobs without managers and that have been sent to user
                userJobQuery = ',' + str(request.user.username)
                print(userJobQuery)
                job_opportunities = JobPost.objects.filter(
                    manager=None, job_offers__icontains=userJobQuery)
                print("job_opportunities")
                print(job_opportunities)

                # Checking if request used post method
                if request.method == 'POST':
                
                    # Creating update profile form with post data
                    update_profile_form = ProfileUpdateFormManager(request.POST or None, request.FILES or None, instance=request.user.profile)
                    
                    # Checking if update profile form is valid
                    if update_profile_form.is_valid():
                        profile = update_profile_form.save(commit=False)
                        profile.user = request.user
                        profile.save()
                        return redirect('dashboard-home')

            # Manager is not evaluated so redirecting to evaluation
            else:
                return redirect('management-evaluation')
        else:
            return redirect('service-complete-profile-manager')
        return render(request, 'dashboard/manager.html', { 'profile': profile, 'job_opportunities':job_opportunities, 'current_jobs' : current_jobs, 'past_jobs' : past_jobs, 'update_profile_form' : update_profile_form, "static_header" : True, "nav_black_link" : True })

# Adding form to view
def jobDetail(request):
    edit_job_form = JobPostForm()
    
    # When job form is posted
    if request.method == 'POST':
        # Creating update profile form with post data
        edit_job_form = JobPostFormUpdate(request.POST, instance=request.user.profile)

    return render(request, 'dashboard/client.html', edit_job_form)

# Class for displaying info about specific job post
class JobDetailView(DetailView):
    model = JobPost
    context_object_name = 'order'
    # template_name = 'dashboard/job_detail.html'
    
    # Overriding the get function to redirect user if not involved in detailed post
    def get(self, request, *args, **kwargs):
        # Getting object
        self.object = self.get_object() 
        user = request.user
        print(user)
        # Checking if user is manager
        if self.template_name == 'dashboard/job_detail_manager.html':
            if not user.profile.is_manager == True:
                return redirect('dashboard-job-detail-manager', pk=self.object.pk)


        # Checking if user is client 
        if self.template_name == 'dashboard/job_detail_client.html':
            if not user.profile.is_client == True:
                return redirect('dashboard-job-detail-manager', pk=self.object.pk)


        if self.object.cancelled == True:
            print('job is cancelled')
            return redirect('dashboard-home')

        # Checking if user is either manager or client
        if user == self.object.client or user == self.object.manager:

            # Checking if job is not paid
            if self.object.paid_for == False:
                # Redirecting to confirm screen
                return redirect('dashboard-confirm-job', pk=self.object.pk)

            # Returning super
            return super(JobDetailView, self).get(request, *args, **kwargs)
            
        else:
            return redirect('dashboard-home')

    # Overriding django function to change context
    def get_context_data(self, **kwargs):
        context = super(JobDetailView, self).get_context_data(**kwargs)
        
        # Defining manager and client profiles
        manager_name = context['object'].manager
        client_name = context['object'].client
        
        # Calculating total post per day
        length = context['object'].length
        instagram = context['object'].instagram
        facebook = context['object'].facebook


        # Counting unread messages
        if context['object']:
            unread_manager = number_of_unread_messages(context['object'].manager, context['object'].job_id)
            unread_client = number_of_unread_messages(context['object'].client, context['object'].job_id)

        # Calculating number of platforms
        platforms = 0
        if instagram == True:
            platforms+=1
        if facebook == True:
            platforms+=1

        # Calculating post per day
        numberOfPost = context['object'].number_of_post
        print("Total posts " , numberOfPost*platforms)
        print("Length  ", length)
        postPerDay = round((numberOfPost*platforms)/length)
        postPerDayPlatform = round(numberOfPost/length)

        # Creating time left for job preparation
        jobPrepDeadline = context['object'].job_preparation_deadline
        now = datetime.now(timezone.utc)
        jobPrepTimeLeft = jobPrepDeadline - now
        jobPrepTimeLeft = jobPrepTimeLeft.total_seconds()
        print("Secs  " , jobPrepTimeLeft)
        jobPrepMinLeft = jobPrepTimeLeft/60
        JobPrepHourLeft = jobPrepMinLeft/60

        print('Hours: ', JobPrepHourLeft)
        JobPrepDaysRemaining = JobPrepHourLeft/24
        print('days', JobPrepDaysRemaining)
        JobPrepHoursRemaining = JobPrepHourLeft/24
        JobPrepHoursRemaining = int((JobPrepHoursRemaining - int(JobPrepHoursRemaining))*24)

        if JobPrepDaysRemaining < 1:
            JobPrepTimeLeftStr = str(round(JobPrepHoursRemaining)) + " hours left"
            print('JobPrepTimeLeftStr: ', JobPrepTimeLeftStr)
        else:
            # Checking for certain situations
            daysString = " Days left and "
            if int(JobPrepDaysRemaining) == 1:
                daysString = " Day left and "

            hoursString = " hours left"
            if JobPrepHoursRemaining == 1:
                hoursString = " hour left"

            JobPrepTimeLeftStr = str(int(
                JobPrepDaysRemaining)) + daysString + str(JobPrepHoursRemaining) + hoursString

        # Getting profiles and checking if user is assigned
        if manager_name:
            manager_profile = Profile.objects.get(user=manager_name)
        else:
            manager_profile = None
        client_profile = Profile.objects.get(user=client_name)
        
        # Defining and saving form to context
        form = milestoneUpdate()
        context['form'] = form

        # Getting and saving milestones
        milestones = Milestone.objects.filter(job=context['object'])
        context['milestones'] = milestones

        # Applying found data to context
        context['manager_profile'] = manager_profile
        context['client_profile'] = client_profile

        # Applying additional info
        context['job_prep_days_left'] = JobPrepTimeLeftStr
        context['post_per_day'] = postPerDay
        context['post_per_day_platform'] = postPerDayPlatform

        # Adding additional context for styling
        context['static_header'] = True
        context['nav_black_link'] = True

        # Adding unread messages
        context['unread_manager'] = unread_manager
        context['unread_client'] = unread_client

        # Adding edit profile form
        context['edit_job_form'] = JobPostFormUpdate(instance=context['object'])

        return context

    # Func for when job form is posted
    def post(self, request, *args, **kwargs):
        self.object = self.get_object() 
        
        # Getting template name
        print("self.template_name")
        print(self.template_name)
        
        # Getting job for job complete bool update
        job = JobPost.objects.get(pk=self.object.pk)

        # Checking if it is client view
        if self.template_name == 'dashboard/job_detail_client.html':
            
            # Getting data from request
            starNumber = int(request.POST['star-number'])
            milestoneNumber = int(request.POST['milestones'])

            # Getting milestone
            milestone = Milestone.objects.get(job=job, milestone_number=milestoneNumber)



            # Preparing for email by getting vars
            client = job.client
            client = User.objects.get(username=client)
            manager = job.manager
            manager = User.objects.get(username=manager)

            # Defining emails vars
            client_email = client.email
            manager_email = manager.email
            
            # Getting users usernames
            manager = job.manager.username
            client = job.client.username


            if milestoneNumber == 1:
                print(starNumber)
                milestone.milestone_rating = starNumber

                # Sending out email to manager about rating
                milestoneRatedEmail(manager, client, manager_email, milestoneNumber, starNumber)

            elif milestoneNumber == 2:
                milestone.milestone_rating = starNumber
                milestoneRatedEmail(manager, client, manager_email, milestoneNumber, starNumber)

            elif milestoneNumber == 3:
                milestone.milestone_rating = starNumber
                milestoneRatedEmail(manager, client, manager_email, milestoneNumber, starNumber)

            elif milestoneNumber == 4:
                milestone.milestone_rating = starNumber
                milestoneRatedEmail(
                    manager, client, manager_email, milestoneNumber, starNumber)

            milestone.save()

            return redirect('dashboard-job-detail-client', pk=self.object.pk)

        # Getting form with requested data
        form = milestoneUpdate(self.request.POST, self.request.FILES, instance=self.object)
        
        print(form.errors)
        
        # Checking if form is valid
        if form.is_valid():
            
            # Getting milestone vars
            milestone_number = request.POST['milestone-number']
            milestone_statement = request.POST['milestone_statement']
            try:

                milestone_post_goal_completed = request.POST['milestone_post_goal_completed']
            except Exception as e:
                print(e)
                milestone_post_goal_completed = False
            
            # Changing checkbox var
            if milestone_post_goal_completed == 'on':
                milestone_post_goal_completed = True
            else:
                milestone_post_goal_completed = False

            # Saving milestones
            milestone = Milestone.objects.get(job=job, milestone_number=milestone_number)

            milestone.milestone_statement = milestone_statement
            milestone.milestone_post_goal_completed = milestone_post_goal_completed
            milestone.active = False
            milestone.save()

            # Checking if milestone is done for the
            if int(milestone_number) == 3 and int(job.length) == 3:
                # Higher milestone couldn't be updated
                job.job_complete = True
                job.save()
            
            elif int(milestone_number) > 3 and int(job.length) > 3:
                # Higher milestone couldn't be updated
                job.job_complete = True
                job.save()
            else:
                # Trying to apply milestone
                try:
                    # Updating next milestone as active
                    milestone_number = int(milestone_number) + 1
                    milestone = Milestone.objects.get(job=job, milestone_number=milestone_number)
                    milestone.active = True
                    milestone.save()
                except Exception as e:
                    print(e)

        return redirect('dashboard-job-detail-manager', pk=self.object.pk)

class ConfirmJobDetailView(DetailView):
    model = JobPost
    context_object_name = 'order'
    template_name = 'dashboard/confirm_job.html'
    
    # Overriding the get function to redirect user if not involved in detailed post
    def get(self, request, *args, **kwargs):
        
        # Getting object
        self.object = self.get_object() 
        user = request.user

        if self.object.length != 3:
            print('yay')
        else:
            print('ooof')
        if self.object.paid_for == False:
            # Checking if user is either manager or client
            if user == self.object.client or user == self.object.manager:
                # Returning super
                return super(ConfirmJobDetailView, self).get(request, *args, **kwargs)
        # Returning if conditions aren't satisfied
        return redirect('dashboard-home')
        

            

    # Overriding django function to change context
    def get_context_data(self, **kwargs):
        context = super(ConfirmJobDetailView, self).get_context_data(**kwargs)

        # Defining manager and client profiles
        manager_name = context['object'].manager
        manager_profile = Profile.objects.filter(user=manager_name)
        user = self.request.user
        client_profile = self.request.user.profile
        
        # Applying found data to context
        context['manager_profile'] = manager_profile
        context['client_profile'] = client_profile

        # Adding additional context for styling
        context['static_header'] = True
        context['nav_black_link'] = True

        # Adding edit profile form
        context['edit_job_form'] = JobPostFormUpdate(instance=context['object'])

        return context

# Delete user function
def deleteJob(request, pk):
    # Getting job
    job = get_object_or_404(JobPost, pk=pk)

    # Defining user
    user = request.user

    # Defining profile
    profile = request.user.profile

    # Checking if user is involved in job
    if user == job.client or user == job.manager:
        
        # Sending cancelled email
        
        # Getting vars
        manager = job.manager
        manager = User.objects.get(username=manager)
        manager_email = manager.email
        manager = manager.username

        client = job.client
        client = User.objects.get(username=client)
        client_email = client.email
        client = client.username
        
        jobCancelledEmail(manager, client, client_email, manager_email)

        # Cancelling the job
        job.cancelled = True
        job.active = False
        job.save()
        
        # Making client non busy
        client = Profile.objects.get(user=job.client)
        client.busy = False
        client.save()

    return redirect('dashboard-home')

# Func to change job prep bool
def jobPrepEnded(request, pk):
    # Getting job
    job = get_object_or_404(JobPost, pk=pk)

    # Defining user
    user = request.user

    # Changing variable in db
    job.job_preparation_completed = True
    
    # Changing job deadline
    job.deadline = datetime.now() + timedelta(days=int(job.length))

    # Saving job
    job.save()

    # Getting vars
    manager = job.manager
    manager = User.objects.get(username=manager)
    manager = manager.username

    client = job.client
    client = User.objects.get(username=client)
    client_email = client.email
    client = client.username
    
    jobPrepEndedEmail(manager, client, client_email)

    # Creating milestone emails timing variables
    if job.length == 14:

        # Defining day after amount for milestone emails
        milestoneOneWarningDate = timedelta(days=2)
        milestoneOneDueDate = timedelta(days=3)

        milestoneTwoWarningDate = timedelta(days=6)
        milestoneTwoDueDate = timedelta(days=7)

        milestoneThreeWarningDate = timedelta(days=9)
        milestoneThreeDueDate = timedelta(days=10)

        milestoneFourWarningDate = timedelta(days=9)
        milestoneFourDueDate = timedelta(days=14)
    elif job.length == 10:

        # Defining day after amount for milestone emails
        milestoneOneWarningDate = timedelta(days=1)
        milestoneOneDueDate = timedelta(days=2)

        milestoneTwoWarningDate = timedelta(days=3)
        milestoneTwoDueDate = timedelta(days=4)

        milestoneThreeWarningDate = timedelta(days=6)
        milestoneThreeDueDate = timedelta(days=7)

        milestoneFourWarningDate = timedelta(days=6)
        milestoneFourDueDate = timedelta(days=10)
    elif job.length == 7:

        # Defining day after amount for milestone emails
        milestoneOneWarningDate = timedelta(days=1)
        milestoneOneDueDate = timedelta(days=2)

        milestoneTwoWarningDate = timedelta(days=2)
        milestoneTwoDueDate = timedelta(days=3)

        milestoneThreeWarningDate = timedelta(days=4)
        milestoneThreeDueDate = timedelta(days=5)

        milestoneFourWarningDate = timedelta(days=6)
        milestoneFourDueDate = timedelta(days=7)

    elif job.length == 5:

        # Defining day after amount for milestone emails
        milestoneOneWarningDate = timedelta(days=1)
        milestoneOneDueDate = timedelta(days=2)

        milestoneTwoWarningDate = timedelta(days=2)
        milestoneTwoDueDate = timedelta(days=3)

        milestoneThreeWarningDate = timedelta(days=3)
        milestoneThreeDueDate = timedelta(days=4)

        milestoneFourWarningDate = timedelta(days=4)
        milestoneFourDueDate = timedelta(days=5)

    elif job.length == 3:
        # Defining day after amount for milestone emails
        milestoneOneWarningDate = timedelta(days=1)
        milestoneOneDueDate = timedelta(days=2)

        milestoneTwoWarningDate = timedelta(days=2)
        milestoneTwoDueDate = timedelta(days=3)

        milestoneThreeWarningDate = timedelta(days=3)
        milestoneThreeDueDate = timedelta(days=4)

    print('how\n\n\n\n\n\n\n')

    # Scheduling emails
    milestone_send_emails.apply_async(
        (job.id, 1, True), eta=datetime.now() + milestoneOneWarningDate)
    milestone_send_emails.apply_async(
        (job.id, 1, False), eta=datetime.now() + milestoneOneDueDate)
    milestone_send_emails.apply_async(
        (job.id, 2, True), eta=datetime.now() + milestoneTwoWarningDate)
    milestone_send_emails.apply_async(
        (job.id, 2, False), eta=datetime.now() + milestoneTwoDueDate)
    milestone_send_emails.apply_async(
        (job.id, 3, True), eta=datetime.now() + milestoneThreeWarningDate)
    milestone_send_emails.apply_async(
        (job.id, 3, False), eta=datetime.now() + milestoneThreeDueDate)

    # Checking if job length is large enough for 4 milestones
    print("job.length")
    print(job.length)
    if job.length != 3:
        milestone_send_emails.apply_async(
            (job.id, 4, True), eta=datetime.now() + milestoneFourWarningDate)
        milestone_send_emails.apply_async(
            (job.id, 4, False), eta=datetime.now() + milestoneFourDueDate)
    else:
        print('short job')

    print('Works')
    return redirect('dashboard-job-detail-manager', pk=pk)


def number_of_unread_messages(user, job):
    
    # Getting unread messages by job
    job_id = 'chat_' + job
    message_number = Message.objects.filter(
        job=job_id, recipient_viewed=False).exclude(author=user).count()
    print('message_number')
    print(message_number)

    # If message number over certain amount we may send email

    return message_number
    
