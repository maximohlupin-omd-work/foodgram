from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color',)


admin.site.register(Tag, TagAdmin)
