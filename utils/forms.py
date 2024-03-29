from django import forms

class ValidateEmailFieldForm(forms.Form):
    data = forms.EmailField(max_length=500)

class ValidateShortTextFieldForm(forms.Form):
    data = forms.CharField(max_length=250)

class ValidateLongTextFieldForm(forms.Form):
    data = forms.CharField(max_length=1500)

class ValidateNumberFieldForm(forms.Form):
    data = forms.IntegerField()

class ValidateFloatFieldForm(forms.Form):
    data = forms.FloatField()

class ValidateDateFieldForm(forms.Form):
    data = forms.DateField()

class ValidateDateTimeFieldForm(forms.Form):
    data = forms.DateTimeField()

class ValidateTimeFieldForm(forms.Form):
    data = forms.TimeField()


class ValidateDurationFieldForm(forms.Form):
    data = forms.DurationField()

class ValidateFileFieldForm(forms.Form):
    data = forms.FileField()

class ValidateImageFieldForm(forms.Form):
    data = forms.ImageField()

class ValidateChoicesFieldForm(forms.Form):
    data = forms.CharField(max_length=250)
    def __init__(self, data=None, choices=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        choices = [choice.name for choice in choices]
    
        if data['data'] not in choices :
            self.add_error("data", "this choice must a be a valide one")
      
        

       
       
        
       