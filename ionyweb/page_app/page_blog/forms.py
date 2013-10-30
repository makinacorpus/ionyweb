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


class PageApp_BlogForm(ModuloModelForm):

    class Meta:
        model = PageApp_Blog


class EntryForm(ModuloModelForm):
    author = forms.ModelChoiceField(label=_('author'),
                                    queryset=User.objects.all(), 
                                    empty_label=None)

    def __init__(self, authors_choices, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['author'].choices = authors_choices

    class Meta:
        model = Entry
        exclude = ('blog', 'thumb')
        widgets = {
            'publication_date': DateTimePicker,
            'body': TinyMCELargeTable(attrs={'cols': 80, 'rows': 15,}),
            'slug': SlugWidget('title'),
            'image': FileManagerWidget,
        }


class EntrySearch(forms.Form):
    date = forms.DateField(required=False)
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Recherche libre : mot clés'}))

    def __init__(self, *args, **kwargs):
        super(EntrySearch, self).__init__(*args, **kwargs)
        for name, field in self.fields.iteritems():
            field.widget.attrs['class'] = 'form-control'


class FrontEntryForm(forms.ModelForm):

    body = forms.CharField(widget=TinyMCE(mce_attrs=settings.TINYMCE_FRONTEND_CONFIG), label=u'Corps')

    class Meta:
        model = Entry
        fields = (
            'title',
            'resume',
            'body',
            'thumb',
            'tags',
        )

    def __init__(self, *args, **kwargs):
        super(FrontEntryForm, self).__init__(*args, **kwargs)
        self.fields['tags'].help_text = u'Entrez des mots-clés séparés par une virgule.'
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'title',
            'resume',
            'body',
            'thumb',
            'tags',
        )
