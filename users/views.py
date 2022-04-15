from django.shortcuts import redirect, render

from django.http import HttpResponseRedirect

# Importing login func from django
from django.contrib.auth import authenticate, login, logout

# Importing Authentication Form
from django.contrib.auth.forms import AuthenticationForm

# importing messages from django
from django.contrib import messages

# Importing email functions
from django.core.mail import EmailMessage

# Importing to handle Url
from django.urls import reverse
from urllib.parse import urlencode

# importing User Registeraton Form
from .forms import UserRegisterForm, ProfileUpdateFormClient, ProfileUpdateFormManager

# Importing Profile Modal
from .models import Profile

# Importing Evaluation Modal
from management.models import ManagerEvaluation, ManagerPreference

# Importing needed libs for email verification
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from webapp.tokens import token_generation

# Importing local tasks
from .tasks import userCreationOneDayCheckin

# Importing the datetime
from datetime import timedelta, datetime

from django.contrib.auth import views as auth_views

# Importing lib to hash password
from django.contrib.auth.hashers import make_password
# Registering new user
def registerFunc(request):
    if request.method == 'POST':

        # Getting posted data in form
        form = UserRegisterForm(request.POST)

        # Checking if form is valid
        if form.is_valid():
            # Changing is active bool in database to false before committing
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Getting username and email to create message and confirm email
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            # Getting current site
            current_site = get_current_site(request)
            mail_subject = 'Activate your iBlinkco account.'
            
            # Creating message body and rendering from template
            messageBody = render_to_string('users/activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generation.make_token(user),
            })

            # Creating thank you message
            messages.success(
                request, f'Congratulations {username} you created an account for iBlinkco! Please confirm your email address to complete the registration')

            # Sending email 
            email = EmailMessage(mail_subject,
                                 messageBody, to=[f'{email}'])
            print(email)
            # email.send()
            
            print('Verification email sent')

            # Redirecting to login screen
            url = request.POST.get("current-path")
            url = createUrl('login', url)
            return redirect(url)
        else:
            print("form.errors")
            print(form.errors.as_data())

            # Creating a list to store formatted errors
            errorList = []

            # Looping through list of errors, formatting and appending them
            for error in form.errors.as_data():
                for singleError in form.errors[error].as_data():
                    print(singleError)
                    print("singleError")
                    errorList.append((str(singleError)[2:])[:-2])

            # Looping through errorList to return messages
            for error in errorList:
                messages.warning(request, error)
            

            # Redirecting to signup screen
            url = request.POST.get("current-path")
            url = createUrl('login', url)
            return redirect(url)

    # Redirecting to signup screen
    url = createUrl('signup', 'homepage-home')
    return redirect(url)

# Activate account function
def activate(request, uidb64, token):
    try:
        # Decoding encoded user id
        uid = force_text(urlsafe_base64_decode(uidb64))

        # Getting user
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and token_generation.check_token(user, token):

        # Changing value of 
        user.is_active = True
        user.save()
        login(request, user)

        # Scheduling oneday checkin email
        userCreationOneDayCheckin.apply_async(
            (uid,), eta=datetime.now() + timedelta(days=1))

        # return redirect('home')
        messages.success(request, f'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.warning(request, f'Activation link is invalid!')

    # Redirecting to login screen
    return redirect('homepage-overview')

# Login function
def loginFunc(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print(user)
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get("next"))
            else:
                return redirect('dashboard-home')
        else:
            # Redirecting to signup screen
            messages.warning(request, f'There was a problem logging in your account')
            url = request.POST.get("current-path")
            url = createUrl('login', url)
            return redirect(url)
    else:
        form = AuthenticationForm()
    return redirect('homepage-home')

# Logout function
def logoutFunc(request):
    # user = request.user
    logout(request)
    return redirect('dashboard-home')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get("username")
        print("email\n\n\n\n\n\n\n\n\n")
        print(email)
        # Checking if account with email exist

        try:
            user = User.objects.get(email=email)

            # Getting current site
            current_site = get_current_site(request)
            mail_subject = 'iBlinkco Forgot Password'

            # Creating message body and rendering from template
            messageBody = render_to_string('users/password_templates/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generation.make_token(user),
            })

            print('sdsds')
            # Sending email
            email = EmailMessage(mail_subject,
                                 messageBody, to=[f'{email}'])
            print(email)
            email.send()
            
            messages.success(
                request, f'Verification email sent')
        except Exception as e:
            print(e)
            messages.warning(
                request, f'Email is not connected to an account')

    url = request.POST.get("current-path")
    url = createUrl('forgot_password', url)
    return redirect(url)

# Reset pass access
def forgotPasswordConfirm(request, uidb64, token):

    # Checking if user is 
    if request.method == 'POST':
        
        
        # Getting posted fields
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        url = request.POST.get("current-path")

        print(token)

        # Validating password
        if password != confirm_password:
            print('qqssaaasdsds')
            messages.warning(request, f"Passwords don't match")
            return redirect('users-forgot-password-generator', uidb64=uidb64, token=token)
        elif len(password) < 8:
            print('sdsds')
            messages.warning(request, f"Password is too short")
            return redirect('users-forgot-password-generator', uidb64=uidb64, token=token)
        else:
            print('good')

            # Trying to see if link is valid
            try:
                # Decoding encoded user id
                uid = force_text(urlsafe_base64_decode(uidb64))
                
                print(uid)
                
                # Getting and changing password
                user = User.objects.get(pk=uid)
                password = make_password(password)
                user.password = password
                user.save()

                messages.success(request, f"Password Reset!")

                url = createUrl('login', 'dashboard-home')
                return redirect(url)
            except Exception as e:
                print(e)
    # Trying to see if link is valid
    try:
        print('lllsdsdsds')
        # Decoding encoded user id
        uid = force_text(urlsafe_base64_decode(uidb64))

        # Getting user
        user = User.objects.get(pk=uid)
    except Exception as e:
        print(e)
        user = None
    if user is not None and token_generation.check_token(user, token):

        # return redirect('home')
        messages.success(request, f'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.warning(request, f'Activation link is invalid!')
        return redirect('homepage-home')

    # Redirecting to login screen
    return render(request, 'users/password_templates/password_reset_form.html', {"nav_black_link": True})

# PROFILE FUNC

# Choose type of user function
def comfirmUser(request):
    if request.method == 'POST':

        managerOrClient = request.POST.get("if-manager-or-client")

        # Getting user
        profile = request.user.profile

        # If Client
        if managerOrClient == 'True':

            # Changing value of manager type
            profile.is_manager = False
            profile.is_client = True

            # Saving value in db
            profile.save(update_fields=["is_manager", "is_client"])
            
            # Checking if evaluation is already created if so deleting it
            try:
                evaluation = ManagerEvaluation.objects.get(manager=request.user)
                evaluation.delete()
            except ManagerEvaluation.DoesNotExist:
                print('does not exists')
            

            # Redirecting 
            return redirect('service-complete-profile-client')
        # If Manager
        else:
            # Changing value of manager type
            profile.is_manager = True
            profile.is_client = False
            
            # Saving value in db
            profile.save(update_fields=["is_manager", "is_client"]) 

            try:
                evaluation = ManagerEvaluation.objects.get(manager=request.user)
            except ManagerEvaluation.DoesNotExist:
                evaluation = ManagerEvaluation.objects.create(manager=request.user)
            
            
            # Creating evaluation modal for managers
            evaluation = ManagerEvaluation.objects.get(manager=request.user)

            # Creating manager preferences
            manager_preferences = ManagerPreference.objects.create(
                manager=request.user)

            # Redirecting 
            return redirect('service-complete-profile-manager')

        
        return redirect('homepage-home')

# Function to create url with paramaters
def createUrl(state, url):
    base_url = reverse(url)
    if state == 'login':
        query_string =  urlencode({'login': 'true'})
    elif state == 'signup':
        query_string =  urlencode({'signup': 'true'})
    else:
        query_string = urlencode({state: 'true'})
    url = '{}?{}'.format(base_url, query_string) 
    return url
