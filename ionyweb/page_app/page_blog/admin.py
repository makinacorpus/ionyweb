# -*- coding: utf-8 -*-
"""
Administration interface options of ``blog`` application.
"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ionyweb.page_app.page_blog.models import PageApp_Blog, Entry

class EntryAdmin(admin.ModelAdmin):
    """
    Administration interface options of ``Entry`` model.
    """
    list_display = ('title', 'page', 'status', 'author', 'a_la_une')
    #list_filter = ('blog__page__title', )
    search_fields = ('title', 'body', 'resume')
    date_hierarchy = 'publication_date'
    fieldsets = (
        (_('Headline'), {'fields': ('blog', 'author', 'title', 'slug', 'tags')}),
        (_('Publication'), {'fields': ('publication_date', 'status', 'a_la_une')}),
        (_('Body'), {'fields': ('body',)}),
    )
    save_on_top = True
    radio_fields = {'status': admin.VERTICAL}
    prepopulated_fields = {'slug': ('title',)}

    def page(self, obj):
        pages = obj.blog.page.all()
        if pages:
            return pages[0].title

admin.site.register(PageApp_Blog)
admin.site.register(Entry, EntryAdmin)
