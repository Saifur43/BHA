from django import forms
from .models import BHAComponent, BHAConfiguration, BHAConfigurationItem

class BHAComponentForm(forms.ModelForm):
    class Meta:
        model = BHAComponent
        fields = ['name', 'length', 'diameter', 'image', 'manufacturer', 'weight']

class BHAConfigurationForm(forms.ModelForm):
    class Meta:
        model = BHAConfiguration
        fields = ['name']