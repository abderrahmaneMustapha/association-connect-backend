from django import forms

class ValidateEmailFieldForm(forms.Form):
    email = forms.EmailField(max_length=500)

class ValidateShortTextFieldForm(forms.Form):
    text = forms.CharField(max_length=250)

class ValidateLongTextFieldForm(forms.Form):
    text = forms.CharField(max_length=1500)

class ValidateFileFieldForm(forms.Form):
    email = forms.CharField(max_length=1500)

class ValidateImageFieldForm(forms.Form):
    email = forms.CharField(max_length=1500)