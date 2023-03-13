"""

    @ File: urls.py
    @ Date: 10.03.2023
    @ Author: Ohlupin Maxim

"""
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    *router.urls
]
