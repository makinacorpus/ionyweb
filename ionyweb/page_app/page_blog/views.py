# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.date_based import object_detail as django_object_detail
from django.utils.decorators import available_attrs
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from  django.utils.encoding import force_unicode
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
import unicodedata
import re
from django.shortcuts import get_object_or_404

from ionyweb.website.rendering import HTMLRendering
from ionyweb.website.rendering.medias import CSSMedia, JSMedia, JSAdminMedia, RSSMedia
from ionyweb.website.rendering.utils import render_view

from models import PageApp_Blog, Entry
from forms import EntrySearch, FrontEntryForm

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


ACTIONS_MEDIAS = [
    JSAdminMedia('page_blog_actions.js'),
]
EDIT_MEDIA = [
    CSSMedia('tagger/css/coop_tag.css', prefix_file=''),
    JSMedia('tagger/js/jquery.autoSuggest.minified.js', prefix_file=''),
    JSMedia('../_tinymce/compressor/', prefix_file=''),
    CSSMedia('select2/select2.css', prefix_file=''),
    CSSMedia('css/select2-bootstrap3.css', prefix_file=''),
    JSMedia('select2/select2.min.js', prefix_file=''),
]

def entries_queryset_view_to_app(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def __wrapped_view(request, obj, **kwargs):
        dict_args = dict(queryset=obj.online_entries.all())
        dict_args.update(kwargs)

        # '<link rel="alternate" type="application/rss+xml" title="RSS" href="%sp/feed/rss/" />'
        medias = [RSSMedia('%sp/feed/rss/' % obj.get_absolute_url()),]

        if request.is_admin:
            medias += ACTIONS_MEDIAS
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content), medias)
        else:
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content),
                                 medias)
    return __wrapped_view


def index_view(request, page_app):
    form = EntrySearch(request.GET)
    if form.is_valid():
        entries = page_app.online_entries.all()
        if form.cleaned_data['date']:
            date = form.cleaned_data['date']
            entries = entries.filter(publication_date__year=date.year,
                                     publication_date__month=date.month,
                                     publication_date__day=date.day)
        if form.cleaned_data['activity']:
            descendants = form.cleaned_data['activity'].get_descendants(include_self=True)
            entries = entries.filter(activities__in=descendants)
        if form.cleaned_data['theme']:
            entries = entries.filter(themes=form.cleaned_data['theme'])
        if form.cleaned_data['q']:
            entries = entries.filter(
                Q(title__icontains=form.cleaned_data['q']) |
                Q(resume__icontains=form.cleaned_data['q']) |
                Q(body__icontains=form.cleaned_data['q']) |
                Q(tagged_items__tag__name__icontains=form.cleaned_data['q'])
            )
    else:
        entries = Entry.objects.none()
    entries = entries.distinct().order_by('-publication_date')
    paginator = Paginator(entries, 20)
    page = request.GET.get('page')
    try:
        entries_page = paginator.page(page)
    except PageNotAnInteger:
        entries_page = paginator.page(1)
    except EmptyPage:
        entries_page = paginator.page(paginator.num_pages)
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    return render_view('page_blog/index.html',
                       {'object': page_app, 'form': form, 'entries': entries_page,
                        'get_params': get_params.urlencode()},
                       [CSSMedia('tagger/css/coop_tag.css', prefix_file=''),
                        JSMedia('tagger/js/jquery.autoSuggest.minified.js', prefix_file='')] +
                        (ACTIONS_MEDIAS if request.is_admin else []),
                       context_instance=RequestContext(request))


@login_required
def add_view(request, page_app):
    #org = Organization.mine(request)
    #if org is None:
        #return HttpResponseForbidden('Votre compte n\'est pas attaché à une organisation.')
    form = FrontEntryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        entry = form.save(commit=False)
        if 'propose' in request.POST and entry.status == 0:
            entry.status = 2
        entry.blog = page_app
        entry.author = request.user
        entry.slug = unicodedata.normalize('NFKD', entry.title).encode('ascii', 'ignore')
        entry.slug = unicode(re.sub('[^\w\s-]', '', entry.slug).strip().lower())
        entry.slug = re.sub('[-\s]+', '-', entry.slug)
        entry.save()
        form.save_m2m()
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(Entry).pk,
            object_id       = entry.pk,
            object_repr     = force_unicode(entry),
            action_flag     = ADDITION,
        )
        return HttpResponseRedirect('/actualites/p/mes-actualites/')
    return render_view('page_blog/edit.html',
                       {'object': page_app, 'form': form},
                       EDIT_MEDIA + (ACTIONS_MEDIAS if request.is_admin else []),
                       context_instance=RequestContext(request))


@login_required
def delete_view(request, page_app, pk):
    entry = get_object_or_404(Entry, pk=pk, author=request.user)
    LogEntry.objects.log_action(
        user_id         = request.user.pk,
        content_type_id = ContentType.objects.get_for_model(Entry).pk,
        object_id       = entry.pk,
        object_repr     = force_unicode(entry),
        action_flag     = DELETION,
        change_message  = u'Article "%s" supprimé.' % force_unicode(entry)
    )
    entry.delete()
    return HttpResponseRedirect('/actualites/p/mes-actualites/')


@login_required
def update_view(request, page_app, pk):
    entry = get_object_or_404(Entry, pk=pk, author=request.user)
    form = FrontEntryForm(request.POST or None, request.FILES or None, instance=entry)
    if form.is_valid():
        form.save(commit=False)
        if 'propose' in request.POST and entry.status == 0:
            entry.status = 2
        entry.save()
        form.save_m2m()
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(Entry).pk,
            object_id       = entry.pk,
            object_repr     = force_unicode(entry),
            action_flag     = CHANGE,
            change_message  = u'%s modifié pour l\'actualité "%s".' % (get_text_list(form.changed_data, _('and')), force_unicode(entry))
        )
        return HttpResponseRedirect('/actualites/p/mes-actualités/')
    return render_view('page_blog/edit.html',
                       {'object': page_app, 'form': form},
                       EDIT_MEDIA + (ACTIONS_MEDIAS if request.is_admin else []),
                       context_instance=RequestContext(request))


@login_required
def my_view(request, page_app):
    entries = page_app.entries.filter(author=request.user).order_by('-publication_date')
    return render_view('page_blog/my_entries.html',
                       {'object': page_app, 'entries': entries},
                       ACTIONS_MEDIAS if request.is_admin else [],
                       context_instance=RequestContext(request))
