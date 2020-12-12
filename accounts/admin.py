from django.contrib import admin
from .models import *


@admin.register(Association, BaseUser, AssociationType,
                ExpectedAssociationMembersNumber, Member, AssociationGroup,
                AssociationGroupMember)
                
class AssociationAdmin(admin.ModelAdmin):
    pass