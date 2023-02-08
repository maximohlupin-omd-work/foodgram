"""

    @ File: urls.py
    @ Date: 18.12.2022
    @ Author: Ohlupin Maxim

"""
from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^auth/token/(login|logout)/', views.TokenUserAuth.as_view()),
]
