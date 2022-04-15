from django import forms
from .models import JobPost, Milestone
from .choices import *

# Creating form for clients to post jobs


class JobPostForm(forms.ModelForm):

    # Form field vars

    # Job Detail
    length = forms.ChoiceField(label='Job Duration', choices=lengthChoices, widget=forms.Select(
        attrs={'class': 'form-control', 'onchange': 'getPriceTag();'}))
    number_of_post = forms.ChoiceField(label='Post Per Day', choices=postPerDayChoices, widget=forms.Select(
        attrs={'class': 'form-control', 'onchange': 'getPriceTag();'}))

    # Platforms
    instagram = forms.BooleanField(label='Instagram', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'checkPlatformInstagram(this);getPriceTag();'}))
    facebook = forms.BooleanField(label='Facebook', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'checkPlatformFacebook(this);getPriceTag();'}))

    # Platform Usernames
    instagram_username = forms.CharField(label='Instagram Username', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}))
    facebook_username = forms.CharField(label='Facebook Username', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}))

    # Services provided
    captions = forms.BooleanField(label='Create Captions', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'getPriceTag();'}))
    search_for_content = forms.BooleanField(label='Find Relevant Content to post', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'getPriceTag();'}))
    post_for_you = forms.BooleanField(label='Manager Will Post For You', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'getPriceTag();'}))
    engagement = forms.BooleanField(label='Engagement', initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'onclick': 'getPriceTag();'}))
    service_description = forms.CharField(label='Service Description', widget=forms.Textarea(
        attrs={'placeholder': 'Enter ...', 'rows': '6', 'class': 'form-control'}))

    # image = forms.ImageField()

    class Meta:
        model = JobPost
        fields = ["length", "number_of_post", "post_for_you", "engagement", "captions", "search_for_content",
                  "service_description", "instagram_username", "facebook_username", "instagram", "facebook"]

# Creating form for clients to post jobs


class JobPostFormUpdate(forms.ModelForm):
    length = forms.ChoiceField(label='Job Length', choices=lengthChoices,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    number_of_post = forms.ChoiceField(
        label='Post Per Day', choices=postPerDayChoices, widget=forms.Select(attrs={'class': 'form-control'}))

    captions = forms.BooleanField(
        label='Create Captions', initial=True, required=False)
    search_for_content = forms.BooleanField(
        label='Find Relevant Content to post', initial=True, required=False)
    post_for_you = forms.BooleanField(
        label='Manager Will Post For You', initial=True, required=False)
    service_description = forms.CharField(label='Service Description', widget=forms.Textarea(
        attrs={'placeholder': 'Enter ...', 'rows': '5', 'class': 'form-control'}))

    class Meta:
        model = JobPost
        fields = ["length", "number_of_post", "post_for_you", "engagement",
                  "captions", "search_for_content", "service_description"]

# Milestone Update
class milestoneUpdate(forms.ModelForm):
    milestone_statement = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'placeholder': 'Description', 'rows': '10', 'class': 'form-control'}))
    milestone_post_goal_completed = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control', 'style' : 'text-align:left;'}))
    class Meta:
        model = Milestone
        fields = ["milestone_statement", "milestone_post_goal_completed"]
