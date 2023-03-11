"""

    @ File: permissions.py
    @ Date: 12.03.2023
    @ Author: Ohlupin Maxim

"""
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import BasePermission


class IsAuthOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated or request.method in SAFE_METHODS:
            return True
        return False
