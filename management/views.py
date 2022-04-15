# Importing libs for stripe
import requests
import urllib
import stripe

from django.conf import settings

from django.shortcuts import render, redirect

from django.urls import reverse

# importing messages from django
from django.contrib import messages

# Importing profile to access
from users.models import Profile

# Importing job post for job acceptance
from service.models import JobPost

# Importing evaluation modal 
from .models import ManagerEvaluation, ManagerPreference

# Importing evaluation forms
from .forms import *

# Importing management task
from .tasks import manager_job_preperation_email

# Importing login required func
from django.contrib.auth.decorators import login_required

# Importing email functions
from django.core.mail import EmailMessage

# Importing needed libs for job acceptance
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from webapp.tokens import token_generation
from datetime import timedelta, datetime

# Homepage function
@login_required(login_url="/?login=true")
def evaluation(request):
    # Getting profile
    profile = request.user.profile

    # Getting user
    user = request.user

    # Getting evaluation object
    evaluation = ManagerEvaluation.objects.get(manager=user)

    # Checking if user is a manager
    if profile.is_manager == True:

        # Creating list for possible locations of answer_two_img
        answer_img_list = ['application_pics/default.jpeg', 'application_pics/default.jpg', 'default.jpeg', 'default.jpg']

        # Checking if evaluation process has started
        if evaluation.accepted == False:
            if evaluation.evaluation_started == False:

                if request.method == 'POST':
                    print('sfeirjkgerybuguiergu')

                    # Changing value of evaluated bool in db to move on
                    evaluation.evaluation_started = True
                    evaluation.save()

                    # Redirecting
                    return redirect('management-evaluation')
                return render(request, 'management/evaluation_start.html', {"static_header" : True, "nav_black_link" : True })
            
            # On first question
            elif evaluation.answer_one_caption_one == 'none' and evaluation.answer_one_caption_two == 'none' and evaluation.answer_one_caption_three == 'none':
                # Getting form
                form = EvaluationOneForm
                
                if request.method == 'POST':

                    # Getting form with inputed data
                    form = EvaluationOneForm(request.POST, instance=evaluation)

                    # Checking if form is valid
                    if form.is_valid():
                        # Saving form
                        # form.save(commit=False)
                        evaluation = form.save(commit=False)
                        evaluation.manager = request.user
                        evaluation.save()
                    
                    # Redirecting
                    return redirect('management-evaluation')
                print("form")
                return render(request, 'management/evaluation_one.html', {"form": form, "static_header" : True, "nav_black_link" : True })
            
            # On second question
            elif evaluation.answer_two_caption == 'none' and evaluation.answer_two_what_are_problems == 'none' and evaluation.answer_two_img in answer_img_list:
                # Getting form
                form = EvaluationTwoForm

                if request.method == 'POST':

                    # Getting form with inputed data
                    form = EvaluationTwoForm(request.POST or None, request.FILES or None, instance=evaluation)
                    
                    # Checking if form is valid
                    if form.is_valid():
                        
                        # Saving form
                        evaluation = form.save(commit=False)
                        evaluation.manager = request.user
                        evaluation.save()
                    else:
                        print(form.errors)
                    return redirect('management-evaluation')
                
                return render(request, 'management/evaluation_two.html', {"form": form, "static_header" : True, "nav_black_link" : True })
            
            # On third question
            elif evaluation.answer_three_caption == 'none' and evaluation.answer_three_img in answer_img_list:
                # Getting form
                form = EvaluationThreeForm

                if request.method == 'POST':

                    # Getting form with inputed data
                    form = EvaluationThreeForm(request.POST or None, request.FILES or None, instance=evaluation)
                    
                    # Checking if form is valid
                    if form.is_valid():
                        
                        # Saving form
                        evaluation = form.save(commit=False)
                        evaluation.manager = request.user
                        evaluation.save()
                    else:
                        print(form.errors)
                    return redirect('management-evaluation')
                return render(request, 'management/evaluation_three.html', {"form": form, "static_header" : True, "nav_black_link" : True })
            # Last question
            else:
                print("dgnjwerkgijsrgsrtgurtg")

                # Checking evaluation is completed
                if evaluation.evaluation_completed == True:

                    # Checking if job preference is completed
                    manager_preference = ManagerPreference.objects.get(manager=user)
                    print("dgnjwerkgijsrgsrtgurtg")
                    if manager_preference.completed == True:
                        return render(request, 'management/evaluation_complete.html', { "static_header" : True, "nav_black_link" : True } )
                    else:
                        form = ManagerPreferenceForm()
                        if request.method == 'POST':
                            form = ManagerPreferenceForm(
                                request.POST or None, request.FILES or None, instance=manager_preference)

                            print("aaaa")
                            finalListOrder = request.POST.get('final-list-order') 
                            finalListOrder = finalListOrder.replace("&amp;", "&")
                            length = request.POST.get('length')
                            post_per_day = request.POST.get('post_per_day')
                            print(finalListOrder)
                            print(request.POST)
                            
                            # Checking if prefered platform is posted
                            numberOfPlatforms = 0

                            instagram = request.POST.get('instagram')
                            facebook = request.POST.get('facebook')

                            instagramBool = False
                            facebookBool = False
                            
                            if instagram:
                                numberOfPlatforms += 1
                                instagram = True
                            if facebook:
                                numberOfPlatforms += 1
                                facebook = True

                            if numberOfPlatforms == 0:
                                messages.warning(
                                    request, f'Please choose a platform that you prefer to work on before you continue')
                                return redirect('management-evaluation')
                                
                            # Creating obj in database

                            manager_preference.manager = user
                            manager_preference.business_list_order = finalListOrder
                            manager_preference.length = length
                            manager_preference.post_per_day = post_per_day
                            manager_preference.instagram = instagramBool
                            manager_preference.facebook = facebookBool


                            manager_preference.completed = True
                            manager_preference.save()
                            return redirect('management-evaluation')
                        return render(request, 'management/job_preferences.html', {"static_header": True, "nav_black_link": True, "form" : form })

                # Getting language from profile
                language = profile.language
                if language == 'English':
                    language = 'Spanish'
                elif language == 'Spanish':
                    language = 'English'

                if request.method == 'POST':


                    # Getting posted value
                    accepted = request.POST.get('accepted-post')
                    
                    # Converting to bool
                    if accepted == 'True':
                        accepted = True
                    else:
                        accepted = False
                    
                    # Adding to evaluation
                    evaluation.choose_job = accepted
                    evaluation.evaluation_completed = True
                    
                    # Saving evaluation
                    evaluation.save()

                    # Returning function
                    return redirect('dashboard-home')

                return render(request, 'management/evaluation_four.html', { "language" : language, "static_header" : True, "nav_black_link" : True })
        else:
                return redirect('dashboard-home')
    else:
        return redirect('dashboard-home')


# Stripe auth view
def stripeAuthorizeView(request):

    # Checking if user is signed in
    if not request.user.is_authenticated:
        return redirect('dashboard-home')
    
    # Definning stripe oauth url
    url = 'https://connect.stripe.com/oauth/authorize'

    # Creating parameters
    params = {
        'response_type': 'code',
        'scope': 'read_write',
        'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
        # 'redirect_uri': f'http://localhost:8000/users/oauth/callback'
        'redirect_uri': f'https://django-connect.herokuapp.com/users/oauth/callback'
    }

    # Creating final
    url = f'{url}?{urllib.parse.urlencode(params)}'
    return redirect(url)

# Stripe Oauth callback view
def stripeAuthorizeCallbackView(request):
    user = request.user
    code = request.GET.get('code')
    # if not request.user.is_authenticated():
    if code:
        data = {
            'client_secret': settings.STRIPE_SECRET_KEY,
            'grant_type': 'authorization_code',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            'code': code
        }
        url = 'https://connect.stripe.com/oauth/token'
        resp = requests.post(url, params=data)
        print(resp.json())

        # Updating stipe id token in db
        stripe_user_id = resp.json()['stripe_user_id']
        profile = Profile.objects.get(user=user)
        profile.stripe_user_id = stripe_user_id
        profile.save()
            
    response = redirect('dashboard-home')
    return response
    

# Sending manager email
def emailJobOffer(user, job, current_site):
    
    print('sssd')
    # Getting current site
    mail_subject = 'New Job Opportunity!'

    # Creating variables
    
    uid = urlsafe_base64_encode(force_bytes(job.pk))
    token = token_generation.make_token(user)
    messageBody = {
        'user' : user,
        'order': job,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(job.pk)),
        'token': token_generation.make_token(user),
    }

    # Creating strings

    # Creating beginning
    beginning = 'Hello, ' + str(user.username) + ', You have a job opportunity with ' + str(job.client) +', '

    # Creating middle
    middle = '\nJob Details: \n\nServices:'
    
    create_caption = ''
    look_for_content = ''
    if job.captions == True:
        create_caption = '\nCreate Captions'

    if job.search_for_content == True:
        look_for_content = '\nLook for content'

    engagement = ''
    if job.engagement == True:
        engagement = '\nCasual engagement needed'

    length = '\n\nJob Length: ' + str(job.length) + ' days'

    platforms = '\n\nPlatforms:'
    instagram = ''
    facebook = ''

    if job.instagram == True:
        instagram = '\nInstagram'

    if job.facebook == True:
        facebook = '\nFacebook'
    
    job_description = "\n\nDescription:"
    description = "\n" + str(job.service_description)

    middle = middle + create_caption + look_for_content + engagement + \
        length + platforms + instagram + facebook + job_description + description

    client = Profile.objects.get(user=job.client)
    clientDetails = f"\n\nClient Details:\n Name: {client.first_name} {client.last_name} \n Language: {client.language} \n Business Name: {client.business_name} \n Business Type: {client.business_type} \n Business Description: {client.description}"

    accept = '\n\nAccept Job: \n' 
    print("reverse('management-job-offer', args=(uid, token))")
    print(reverse('management-job-offer', args=(uid, token)))
    acceptLink = 'https://www.' + current_site + reverse('management-job-offer', args=(uid, token)) + '?accepted=True\n\n'

    decline = '\n\nDecline Job: \n'
    declineLink = 'https://www.' + current_site + \
        reverse('management-job-offer', args=(uid, token)) + \
        '?accepted=False\n\n'
    
    # Creating ending
    ending = clientDetails + accept + acceptLink + decline + declineLink

    # Creating message
    messageBody = beginning + middle + ending

    print(messageBody)
    # Getting email
    email = user.email
    
    print(email)
    
    # Sending email 
    email = EmailMessage(mail_subject, messageBody, to=[f'{email}'])
    email.send()
    return email

# Manager job offer confirm through email
@login_required(login_url="/?login=true")
def managerOfferConfirmPage(request, job_id):
    assignment = managerOfferConfirm(job_id, request.user)
    job = JobPost.objects.get(job_id=job_id)
    if assignment == 'success':
        messages.success(request, f'You are now assigned to work a job with {job.client}. We will notify when to start the job')
    elif assignment == 'failed':
        messages.warning(request, f'Manager already assigned')
    return redirect('dashboard-home')


# Manager job offer confirm through email
@login_required(login_url="/?login=true")
def managerOfferConfirmEmail(request, uidb64, token):
    
    # Getting accepted arg
    accepted = request.GET.get('accepted')
    print(accepted)
    # Defining user
    user = request.user
    try:
        # Decoding encoded user id
        uid = force_text(urlsafe_base64_decode(uidb64))
        job = JobPost.objects.get(pk=uid)
    except:
        job = None
    
    # Checking if job exists
    if job is not None and token_generation.check_token(user, token):

        # If job is accepted changing bool in db
        if accepted == 'True':
            assignment = managerOfferConfirm(uid, request.user)
            if assignment == 'success':
                messages.success(request, f'You are now assigned to work a job with {job.client}. We will notify when to start the job')
            elif assignment == 'failed':
                messages.warning(request, f'Manager already assigned')

    else:
        messages.warning(request, f'Activation link is invalid!')
    return redirect('dashboard-home')

# Manager offer confirm


def managerOfferConfirm(job_id, user):
    print('sdsdsd')


    job = JobPost.objects.get(job_id=job_id)
    # Checking if manager assigned already
    if not job.manager:

        # Changing variable in db
        job.manager = user
        job.save()
        print(job.id)

        manager_job_preperation_email.apply_async(
            (job.id,), eta=datetime.now() + timedelta(days=2))
        return 'success'

    # Redirecting if manager already assigned
    else:
        return 'failed'
