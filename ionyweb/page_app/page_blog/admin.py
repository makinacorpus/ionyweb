# -*- coding: utf-8 -*-
"""
Administration interface options of ``blog`` application.
"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from chosen import widgets as chosenwidgets

from ionyweb.page_app.page_blog.models import PageApp_Blog, Entry

from tinymce.widgets import AdminTinyMCE


class EntryAdminForm(forms.ModelForm):
    body = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False, label='Contenu')

    class Meta:
        model = Entry
        widgets = {
            'activities': chosenwidgets.ChosenSelectMultiple(),
            'themes': chosenwidgets.ChosenSelectMultiple(),
        }


class EntryAdmin(admin.ModelAdmin):
    """
    Administration interface options of ``Entry`` model.
    """
    form = EntryAdminForm
    list_display = ('title', 'blog', 'status', 'author', 'publication_date', 'a_la_une')
    list_filter = ('status', 'blog', )
    search_fields = ('title', 'body', 'resume')
    date_hierarchy = 'publication_date'
    fieldsets = (
        (_('Headline'), {'fields': ('blog', 'author', 'title', 'slug')}),
        (_('Publication'), {'fields': ('publication_date', 'status', 'a_la_une')}),
        (_('Body'), {'fields': ('resume', 'body', 'thumb')}),
        (_('Classification'), {'fields': ('activities', 'themes', 'tags')}),
    )
    #radio_fields = {'status': admin.VERTICAL}
    prepopulated_fields = {'slug': ('title',)}


class BlogAdmin(admin.ModelAdmin):

    list_display = ('title', 'front_page')

    def front_page(self, obj):
        pages = obj.page.all()
        if pages:
            return pages[0].title
        else:
            return '(non visible sur le site)'
    front_page.short_description = u'Page du site'

admin.site.register(PageApp_Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)
