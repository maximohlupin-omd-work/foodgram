"""

    @ File: utils.py
    @ Date: 13.03.2023
    @ Author: Ohlupin Maxim

"""
import csv

from django.http.response import HttpResponse


def download_csv(queryset, fields):
    response = HttpResponse()
    response['Content-Type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset.values_list(*fields):
        writer.writerow(obj)
    return response
