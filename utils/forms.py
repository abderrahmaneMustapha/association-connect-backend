from django import forms

class ValidateEmailFieldForm(forms.Form):
    data = forms.EmailField(max_length=500)

class ValidateShortTextFieldForm(forms.Form):
    data = forms.CharField(max_length=250)

class ValidateLongTextFieldForm(forms.Form):
    data = forms.CharField(max_length=1500)

class ValidateFileFieldForm(forms.Form):
    data = forms.FileField()

class ValidateImageFieldForm(forms.Form):
    data = forms.ImageField()