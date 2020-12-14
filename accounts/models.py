#django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import FileExtensionValidator

#package
from phonenumber_field.modelfields import PhoneNumberField

#python
import uuid

#me
from .managers import CustomUserManager


# Create your models here.
class BaseUser(AbstractUser):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4)

    username = models.CharField(_("user name"), max_length=120,  null=True, blank=True)
    first_name = models.CharField(_("first name"), max_length=150, null=True)

    last_name = models.CharField(_("last name"), max_length=150, null=True)

    date_birth = models.DateField(_("date of birth"),
                                  auto_now=False,
                                  auto_now_add=False,
                                  null=True)

    email = models.EmailField(_('email adress'), unique=True)

    phone = PhoneNumberField(_("phone number"), null=True)

    description = models.TextField(_("a short description"), null=True)

    adress = models.CharField(_("adress"), max_length=500, null=True)

    city = models.CharField(verbose_name=_("City"), max_length=500, null=True)

    country = models.CharField(verbose_name=_("Country"),
                               max_length=500,
                               null=True)

    is_association_owner = models.BooleanField(
        _("This user is an association owner"), default=False, null=True)

    profile_pic = models.ImageField(
        _('profile pic'),
        upload_to='users/profile_pics',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'svg'])
        ],
        null=True,
        blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
 
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return str(self.email)


class AssociationType(models.Model):
    name = models.CharField(_('name of the association'), max_length=125)
    description = models.TextField(_('description of the association'),
                                   max_length=750)


class ExpectedAssociationMembersNumber(models.Model):
    max_number = models.IntegerField(
        _('expected max number of association members number'))
    min_number = models.IntegerField(
        _('expected min number of association members number'))


class Association(models.Model):
    name = models.CharField(_('name of the association'), max_length=225)
    description = models.TextField(_('description of the association'),
                                   max_length=1500, null=True, blank=True)
    association_type = models.ForeignKey(
        AssociationType,
        verbose_name=_('the association type'),
        on_delete=models.CASCADE)
    association_min_max_numbers = models.ForeignKey(
        ExpectedAssociationMembersNumber,
        verbose_name=_(
            'expected max and min number of association members number'),
        on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta : 
        permissions = (
            ('update_association_info', 'Update association Info'),
            ('view_association_dashboard', 'View association dashboard'),
            ('add_association_member', 'Add an new association member'),
            ('delete_association_member', 'Delete association member'),
            ('view_association_member', 'View association member'),
        )


class Member (models.Model):
    user = models.ForeignKey(BaseUser, verbose_name=_("member"), on_delete=models.CASCADE)
    association = models.ForeignKey(Association , verbose_name=_("association"), on_delete=models.CASCADE)
    is_owner = models.BooleanField(_('is an association owner'), default=False)
    is_archived = models.BooleanField(_('this user is not a member any more'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AssociationMembership(models.Model):
    member = models.ForeignKey(Member, verbose_name=_("member"), on_delete=models.CASCADE)
    membership_time = models.DurationField(_("membership time "))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AssociationGroup(models.Model):
    STATIQUE = 'S'
    DYNAMIQUE = 'D'

    ASSOCIATION_GROUP_TYPE = [(STATIQUE, 'STATIQUE'), (DYNAMIQUE, 'DYNAMIQUE')]
    name = models.CharField(_('name of the group'), max_length=225)
    association = models.ForeignKey(Association , verbose_name=_("association"), on_delete=models.CASCADE)
    group_type = models.CharField(
        max_length=2,
        choices=ASSOCIATION_GROUP_TYPE,
        default=STATIQUE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
                ('add_group_member', 'Add an new group member'),
                ('delete_group_member', 'Delete group member'),
                ('view_group_member_info', 'View group member info'),
                ('update_group_info', 'Update group Info'),
                ('view_group_dashboard', 'View group dashboard'),
                ('delete_group', 'Delete group'),
                ('add_group', 'Add new group')
        )

class AssociationGroupMember(models.Model):
    member = models.ForeignKey(Member, verbose_name=_("member"), on_delete=models.CASCADE)
    group = models.ForeignKey(AssociationGroup, verbose_name=_("association group"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

      