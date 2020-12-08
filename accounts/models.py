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
        _("This user is an association owner"), default=False)

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