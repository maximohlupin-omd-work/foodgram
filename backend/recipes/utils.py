"""

    @ File: utils.py
    @ Date: 13.03.2023
    @ Author: Ohlupin Maxim

"""
import csv

from django.http.response import HttpResponse


def download_csv(queryset):
    opts = getattr(queryset.model, '_meta')
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
