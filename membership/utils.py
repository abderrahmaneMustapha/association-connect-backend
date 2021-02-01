from .models import Choice

def check_choices(html_name, choices, field):
        allowed_choices_fields = ["checkbox", "radio", "select"]
        choices =  [] if not choices else choices
        if (html_name in allowed_choices_fields ):

            if ( len(choices) <= 1):
                raise Exception("check box and radio type must have at least 2 choices")

            else :
                  for id in choices:
                    choice = Choice.objects.get(id=id)
                    field.choices.add(choice)
                                 
              
        else:
            if (len(choices) > 0):
                raise Exception("this field can not have choices")