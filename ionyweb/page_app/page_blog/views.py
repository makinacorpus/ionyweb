# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.views.generic.date_based import object_detail as django_object_detail
from django.utils.decorators import available_attrs
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import RequestContext
from django.db.models import Q

from ionyweb.website.rendering import HTMLRendering
from ionyweb.website.rendering.medias import CSSMedia, JSMedia, JSAdminMedia, RSSMedia
from ionyweb.website.rendering.utils import render_view

from models import PageApp_Blog, Entry
from forms import EntrySearch

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


ACTIONS_MEDIAS = [
    JSAdminMedia('page_blog_actions.js'),
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
        entries = Entry.objects
        if request.GET.get('date'):
            date = form.cleaned_data['date']
            entries = entries.filter(publication_date__year=date.year,
                                     publication_date__month=date.month,
                                     publication_date__day=date.day)
        if request.GET.get('q'):
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
                       (CSSMedia('tagger/css/coop_tag.css', prefix_file=''),
                        JSMedia('tagger/js/jquery.autoSuggest.minified.js', prefix_file='')),
                       context_instance=RequestContext(request))
