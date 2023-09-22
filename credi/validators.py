from django.db import DataError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, password_validation

from rest_framework.utils.representation import smart_repr

from django.utils.translation import gettext_lazy as _

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number

import magic, os, re, string
from pathlib import Path

def validate_possible_number(phone, country=None):
    phone_number = to_python(phone, country)
    if (
        phone_number
        and not is_possible_number(phone_number)
        or not phone_number.is_valid()
    ):
        raise ValidationError(
            "The phone number entered is not valid.", code='invalid'
        )
    return phone_number


def max_filesize(file_, file_size= 1):
    MEGABYTE_LIMIT = file_size
    filesize = file_.size
    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ValidationError("file size should be maximum {0} MB".format( MEGABYTE_LIMIT ))

def qs_exists(queryset):
    try:
        return queryset.exists()
    except (TypeError, ValueError, DataError):
        return False


def qs_filter(queryset, **kwargs):
    try:
        return queryset.filter(**kwargs)
    except (TypeError, ValueError, DataError):
        return queryset.none()

@deconstructible
class FileValidator(object):
    error_messages = {
        'max_size': ("Ensure this file size is not greater than %(max_size)s."
                  " Your file size is %(size)s."),
        'min_size': ("Ensure this file size is not less than %(min_size)s. "
                  "Your file size is %(size)s."),
        'content_type': "Files of type %(content_type)s are not supported.",
        'allowed_extensions': _( "File extension “%(extension)s” is not allowed. " "Allowed extensions are: %(allowed_extensions)s." ),
    }

    def __init__(self, max_size=None, min_size=None, content_types=(), allowed_extensions=None,):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types
        if allowed_extensions is not None:
            allowed_extensions = [
                allowed_extension.lower() for allowed_extension in allowed_extensions
            ]
        self.allowed_extensions = allowed_extensions

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size), 
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'],
                                   'max_size', params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.min_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'], 
                                   'min_size', params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)

            if content_type not in self.content_types:
                params = { 'content_type': content_type }
                raise ValidationError(self.error_messages['content_type'],
                                   'content_type', params)
        
        if self.allowed_extensions:
            extension = Path(data.name).suffix[1:].lower()
            if (
                self.allowed_extensions is not None
                and extension not in self.allowed_extensions
            ):
                raise ValidationError(
                    self.error_messages['allowed_extensions'],
                    params={
                        "extension": extension,
                        "allowed_extensions": ", ".join(self.allowed_extensions),
                        "value": data,
                    },
                )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.max_size == other.max_size and
            self.min_size == other.min_size and
            self.content_types == other.content_types and
            self.allowed_extensions == other.allowed_extensions
        )

@deconstructible
class MobileValidator(object):
    error_messages = {
        'invalid_format': _("Invalid mobile number, check number or country code"),
    }

    def __init__(self, country_code= None):
        self.country_code = country_code

    def __call__(self, data):
        phone_number = to_python( data )
        if self.country_code:
            phone_number = to_python(data, self.country_code)

        if phone_number and not phone_number.is_valid() or not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid_format'])

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.country_code == other.country_code
        )

@deconstructible
class PasswordValidator(object):
    error_messages = {
        'compare': _("Password not matching with compared password"),
    }

    def __init__(self, compare= None):
        self.compare = compare

    def __call__(self, data):
        try:
            password_validation.validate_password(data)
        except ValidationError as e:
            try:
                err = [i for i in e][0]
            except Exception as e:
                err = str( e )
            raise ValidationError( err )
        
        if self.compare:
            pass
        # if re.search('[0-9]', data) == None:
        #     raise ValidationError("it must contain at least one number")
        # if re.search('[a-z]', data) == None:
        #     raise ValidationError("it must contain at least one lowercase letter")
        # if re.search('[A-Z]', data) == None:
        #     raise ValidationError("it must contain at least one uppercase letter")
        # if re.search(f'[{re.escape(string.punctuation)}]', data) == None:
        #     raise ValidationError("it must contain at least one special character")
        
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.compare == other.compare
        )

class UniqueFiledValidator(object):
    """
    Validator that corresponds to `unique=True` on a model field.

    Should be applied to an individual field on the serializer.
    """
    message = _('This field must be unique.')
    requires_context = True

    def __init__(self, queryset, message=None, exclude= None, lookup='iexact'):
        self.queryset = queryset
        self.message = message or self.message
        self.exclude = exclude
        self.lookup = lookup

    def filter_queryset(self, value, queryset, field_name):
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {'%s__%s' % (field_name, self.lookup): value}
        filter_kwargs["is_delete"] = False
        return qs_filter(queryset, **filter_kwargs)

    def exclude_current_instance(self, queryset, instance):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        # if instance is not None :
        #     return queryset.exclude(pk=instance.pk)
        if instance is not None:
            return queryset.exclude(pk=instance)
        return queryset

    def __call__(self, value, serializer_field):
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        #field_name = serializer_field.source_attrs[-1]
        field_name = "__".join( serializer_field.source_attrs )
        # Determine the existing instance, if this is an update operation.
        #instance = getattr(serializer_field.parent, 'instance_id', None)
        try:
            instance_id= serializer_field.parent.context['request'].__dict__['parser_context']['kwargs']['pk']
        except:
            instance_id = None
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset, field_name)
        if self.exclude is not None:
            queryset = self.exclude_current_instance(queryset, instance_id)
        if qs_exists(queryset):
            raise ValidationError(self.message, code='unique')

    def __repr__(self):
        return '<%s(queryset=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        )