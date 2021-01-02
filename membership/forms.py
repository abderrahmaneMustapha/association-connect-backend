from django import forms
from .models import Form

class FormCreationForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = [
             'association', 'title', 'description', 'email', 'start_date',
            'days'
        ]