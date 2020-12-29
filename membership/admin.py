from django.contrib import admin
from .models import *


@admin.register(Form, Costs, UserPayedCosts, FieldType, Field, FieldData,
                FormFilledByUser)
class MembershipAdmin(admin.ModelAdmin):
    pass
