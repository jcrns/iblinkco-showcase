from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import DateInput
from .models import Profile

# User Registration Form
class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        # Fields user needs to sign up
        fields = ['username', 'email', 'password1', 'password2']
    
        # creating custom form by importing UserRegisterForm and adding custom fields
    def getemail(self):
        email = forms.EmailField()



# Creating form for complete profile page
class ProfileUpdateFormClient(forms.ModelForm):
    languagesChoices = (('English', 'English'), ('Spanish', 'Spanish'), ('Chinese', 'Chinese'), ('French', 'French'), ('Other', 'Other'))
    businessTypeChoices = (('Services', 'Services'), ('Retail', 'Retail'), ('Art & Entertainment', 'Art & Entertainment'), ('Tech', 'Tech'), ('Events', 'Events'), ('Farming6', 'Farming'), ('Health Care', 'Health Care'), ('Restaurants', 'Restaurants'), ('Other', 'Other'))
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    language = forms.ChoiceField(label='Language', choices=languagesChoices, widget=forms.Select(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    business_name = forms.CharField(label='Business Name',widget=forms.TextInput(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    business_type = forms.ChoiceField(label='Business Type',choices=businessTypeChoices, widget=forms.Select(attrs={ 'class': 'form-control' }))
    description = forms.CharField(label='Business Description',widget=forms.Textarea(attrs={'placeholder':'Enter ... (max 500 characters)', 'rows' : '5', 'class' : 'form-control' }))
    # image = forms.ImageField()

    def clean_image(self):  
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 4*1024*1024:
                raise ValidationError("Image file too large ( > 4mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "business_name", "business_type", "description", "image", "language"]

class ProfileUpdateFormManager(forms.ModelForm):
    languagesChoices = (('English', 'English'), ('Spanish', 'Spanish'), ('Chinese', 'Chinese'), ('French', 'French'), ('Other', 'Other'))
    businessTypeChoices = (('Services', 'Services'), ('Retail', 'Retail'), ('Art & Entertainment', 'Art & Entertainment'), ('Tech', 'Tech'), ('Events', 'Events'), ('Farming6', 'Farming'), ('Health Care', 'Health Care'), ('Restaurants', 'Restaurants'), ('Other', 'Other'))
    first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    language = forms.ChoiceField(label='Language', choices=languagesChoices, widget=forms.Select(attrs={'placeholder':'Enter', 'class': 'form-control'}))
    description = forms.CharField(label='Profile Bio',widget=forms.Textarea(attrs={'placeholder':'Enter ... (max 500 characters)', 'rows' : '5', 'class' : 'form-control' }))

    def clean_image(self):  
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 4*1024*1024:
                raise ValidationError("Image file too large ( > 4mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "date_of_birth", "description", "image", "language"]
        # Specifying label and widget for dob
        labels = {
            'date_of_birth': ('Date Of Birth'),
        }
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }