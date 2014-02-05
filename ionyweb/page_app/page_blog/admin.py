# -*- coding: utf-8 -*-
"""
Administration interface options of ``blog`` application.
"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.util import flatten_fieldsets
from django.utils.timezone import now
from chosen import widgets as chosenwidgets
from django.contrib.sites.models import Site
from django.conf import settings
from coop_local.mixed_email import send_mixed_email

from ionyweb.page_app.page_blog.models import PageApp_Blog, Entry

from tinymce.widgets import AdminTinyMCE
from haystack import connections


class EntryAdminForm(forms.ModelForm):
    body = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False, label='Contenu')

    def __init__(self, *args, **kwargs):
        super(EntryAdminForm, self).__init__(*args, **kwargs)
        self.fields['publication_date'].initial = now()

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
    list_display = ('title', 'blog', 'status', 'author', 'publication_date', 'a_la_une', 'zoom_sur')
    list_filter = ('status', 'blog', 'a_la_une', 'zoom_sur')
    search_fields = ('title', 'body', 'resume')
    date_hierarchy = 'publication_date'
    change_form_template = 'admin/page_blog/pageapp_blog/tabbed_change_form.html'
    fieldsets = (
        (_('Headline'), {'fields': ('blog', 'author', 'title', 'slug')}),
        (_('Publication'), {'fields': ('publication_date', 'status', 'a_la_une', 'zoom_sur')}),
        (_('Body'), {'fields': ('resume', 'body', 'thumb')}),
        (_('Classification'), {'fields': ('activities', 'themes', 'tags')}),
    )
    restricted_fieldsets = (
        (_('Headline'), {'fields': ('blog', 'author', 'title', 'slug')}),
        (_('Publication'), {'fields': ('publication_date', 'status')}),
        (_('Body'), {'fields': ('resume', 'body', 'thumb')}),
        (_('Classification'), {'fields': ('activities', 'themes', 'tags')}),
    )
    #radio_fields = {'status': admin.VERTICAL}
    prepopulated_fields = {'slug': ('title',)}

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super(EntryAdmin, self).get_fieldsets(request, obj)
        return self.restricted_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Workaround bug http://code.djangoproject.com/ticket/9360 (thanks to peritus)
        """
        return super(EntryAdmin, self).get_form(request, obj, fields=flatten_fieldsets(self.get_fieldsets(request, obj)))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "blog":
            try:
                kwargs['initial'] = PageApp_Blog.objects.get(title='Actualités')
            except PageApp_Blog.DoesNotExist:
                pass
        if db_field.name == "author":
            kwargs['queryset'] = User.objects.order_by('username')
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

    def save_model(self, request, obj, form, change):
        """Send an email if just validated"""
        print 'save'
        if change and obj.status == Entry.STATUS_ONLINE:
            print 'changed V'
            if Entry.objects.get(pk=obj.pk).status != Entry.STATUS_ONLINE:
                print 'old not V'
                from ionyweb.plugin_app.plugin_contact.models import Plugin_Contact
                try:
                    sender = Plugin_Contact.objects.all()[0].email
                except IndexError:
                    sender = None
                dests = obj.author.email
                site = Site.objects.get_current().domain
                subject = u"Votre actualité est publiés sur la plateforme %s" % site
                context = {
                    'site': site,
                    'slug': settings.REGION_SLUG,
                    'entry': obj,
                }
                send_mixed_email(sender, dests, subject, 'email/actu_validation', context)
        super(EntryAdmin, self).save_model(request, obj, form, change)

    class Media:
        js = ('mce_filebrowser/js/filebrowser_init.js',)


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
