"""

    @ File: validators.py
    @ Date: 10.03.2023
    @ Author: Ohlupin Maxim

"""
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


def more_zero_validator(value: int):
    if isinstance(value, int):
        if value < 1:
            raise ValidationError(
                _('%(value)s Должен быть больше единицы'),
                params={'value': value},
            )
    else:
        raise ValidationError(
            _('%(value)s Должен быть целым числом'),
            params={'value': value},
        )
