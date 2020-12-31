from django import forms
from .models  import (Association, AssociationGroup)
class AssociationCreationForm(forms.Form):
    class Meta : 
        model = Association
        fields = [
            'id', 'slug', 'name', 'description', 'association_type',
            'association_min_max_numbers'
        ]