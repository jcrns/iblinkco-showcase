from django.shortcuts import render, redirect

# Importing User Registeraton Form
from users.forms import UserRegisterForm

# Importing Authentication Form
from django.contrib.auth.forms import AuthenticationForm

# Importing profile to access 
from users.models import Profile

# Importing login required func
from django.contrib.auth.decorators import login_required

# Importing evaluation modal 
from management.models import ManagerEvaluation

# Your
from django.contrib.sites.shortcuts import get_current_site

# Homepage function
def home(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    # getting current site and passing in to func
    current_site = get_current_site(request)
    current_site = current_site.domain
    print(current_site)
    return render(request, 'homepage/index.html', {'form_register': form_register, 'form_login' : form_login })

# Overview function
@login_required(login_url="/?login=true")
def overview(request):
    profile = request.user.profile

    # Checking if user has been on the overview
    if profile.is_client == False and profile.is_manager == False:
        return render(request, 'homepage/overview.html', {"nav_black_link" : True} )
    # Redirecting to dashboard
    else:
        return redirect('dashboard-home')
    
# Simple webpages
def termsAndConditions(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/terms-and-conditions.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

def privacyPolicy(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/privacy-policy.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

def partnerships(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/partnerships.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

def helpAndSupport(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/help-and-support.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

def refunds(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/refunds.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

def connectSocials(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    return render(request, 'homepage/share-social-medias.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})

# Become manager page
def becomeManager(request):
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    if request.user.is_authenticated:
    
        if request.user.profile.is_client == True:
            return redirect('service-job')
    return render(request, 'homepage/become-a-manager.html', {"nav_black_link": True, 'form_register': form_register, 'form_login': form_login})
