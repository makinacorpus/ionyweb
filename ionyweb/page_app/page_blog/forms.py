# -*- coding: utf-8 -*-

from datetime import datetime
import floppyforms as forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from ionyweb.forms import ModuloModelForm
from ionyweb.widgets import DatePicker
from models import Entry, PageApp_Blog
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from tinymce.widgets import TinyMCE

from ionyweb.widgets import DateTimePicker, SlugWidget, DatePicker, TinyMCELargeTable
from ionyweb.file_manager.widgets import FileManagerWidget

from coop_local.models import ActivityNomenclature, TransverseTheme


class PageApp_BlogForm(ModuloModelForm):

    class Meta:
        model = PageApp_Blog


class EntrySearch(forms.Form):
    date = forms.DateField(required=False)
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(level=0), empty_label=u'Tout voir', required=False)
    theme = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), empty_label=u'Tout voir', required=False)
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Recherche libre : mot clés'}))

    def __init__(self, *args, **kwargs):
        super(EntrySearch, self).__init__(*args, **kwargs)
        for name, field in self.fields.iteritems():
            field.widget.attrs['class'] = 'form-control'


class FrontEntryForm(forms.ModelForm):

    body = forms.CharField(widget=TinyMCE(mce_attrs=settings.TINYMCE_FRONTEND_CONFIG), label=u'Contenu')

    class Meta:
        model = Entry
        fields = (
            'title',
            'resume',
            'body',
            'thumb',
            'tags',
            'activities',
            'themes',
        )

    def __init__(self, *args, **kwargs):
        super(FrontEntryForm, self).__init__(*args, **kwargs)
        self.fields['tags'].help_text = u'Entrez des mots-clés séparés par une virgule.'
        self.fields['activities'].help_text = u''
        self.fields['themes'].help_text = u''
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'title',
            'resume',
            'body',
            'thumb',
            'tags',
            'activities',
            'themes',
        )
