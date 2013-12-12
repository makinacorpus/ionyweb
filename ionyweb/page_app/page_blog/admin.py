# -*- coding: utf-8 -*-
"""
Administration interface options of ``blog`` application.
"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.models import User
from chosen import widgets as chosenwidgets

from ionyweb.page_app.page_blog.models import PageApp_Blog, Entry

from tinymce.widgets import AdminTinyMCE
from haystack import connections


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
    list_display = ('title', 'blog', 'status', 'author', 'publication_date', 'a_la_une', 'en_direct', 'zoom_sur')
    list_filter = ('status', 'blog', 'a_la_une', 'en_direct', 'zoom_sur')
    search_fields = ('title', 'body', 'resume')
    date_hierarchy = 'publication_date'
    change_form_template = 'admin/page_blog/pageapp_blog/tabbed_change_form.html'
    fieldsets = (
        (_('Headline'), {'fields': ('blog', 'author', 'title', 'slug')}),
        (_('Publication'), {'fields': ('publication_date', 'status', 'a_la_une', 'en_direct', 'zoom_sur')}),
        (_('Body'), {'fields': ('resume', 'body', 'thumb')}),
        (_('Classification'), {'fields': ('activities', 'themes', 'tags')}),
    )
    #radio_fields = {'status': admin.VERTICAL}
    prepopulated_fields = {'slug': ('title',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "blog":
            try:
                kwargs['initial'] = PageApp_Blog.objects.get(title='Actualités')
            except PageApp_Blog.DoesNotExist:
                pass
        if db_field.name == "author":
            kwargs['queryset'] = User.objects.filter(is_staff=True).order_by('username')
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
            kwargs['initial'] = request.user
        field = super(EntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "author":
            field.label_from_instance = lambda(obj): "%s (%s %s)" % (obj.username, obj.first_name, obj.last_name)
        return field

    def queryset(self, request):
        qs = super(EntryAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(author=request.user)
        return qs

    def save_related(self, request, form, formsets, change):
        super(EntryAdmin, self).save_related(request, form, formsets, change)
        ui = connections.all()[0].get_unified_index()
        ui.get_index(Entry).update_object(instance=form.instance)


class BlogAdmin(admin.ModelAdmin):

    list_display = ('front_page', 'title')

    def front_page(self, obj):
        pages = obj.page.all()
        if pages:
            return pages[0].title
        else:
            return '(non visible sur le site)'
    front_page.short_description = u'Page du site'

admin.site.register(PageApp_Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)
