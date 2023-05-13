"""

    @File: validators.py
    @Date: 13.05.2023
    @Author: Ohlpin Maxim

"""
from rest_framework.exceptions import ValidationError


def positive_value_validator(list_value, field) -> None:
    """
        Валидатор списка значений на наличие только позитивеных эллементов
    :param list_value: список эллементов
    :param field: ключ поля для проверки
    :return: None
    """

    err_message = "Убедитесь, что это значение больше либо равно 1."
    len_list_value = len(list_value)

    for i, value in enumerate(list_value):
        if int(value[field]) < 1:
            raise ValidationError(
                detail=[
                    dict() if j != i else {field: [err_message, ]} for j in range(len_list_value)
                ],
                code=None
            )
