# -*- coding: utf-8 -*-
"""
URLs of ``blog`` application.
"""
from django.conf.urls import patterns, url

import django.views.generic
import django.views.generic.list_detail
from views import (entries_queryset_view_to_app, index_view, add_view,
    update_view, delete_view, my_view, feedback_view)
from feeds import RssEntries, RssTag

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
        entries_queryset_view_to_app(django.views.generic.date_based.object_detail),
        dict(
            month_format='%m',
            date_field='publication_date',
            slug_field='slug',
        ),
        name='blog_entry',
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        entries_queryset_view_to_app(django.views.generic.date_based.archive_day),
        dict(
            month_format='%m',
            date_field='publication_date',
        ),
        name='blog_day',
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        entries_queryset_view_to_app(django.views.generic.date_based.archive_month),
        dict(
            month_format='%m',
            date_field='publication_date',
        ),
        name='blog_month',
    ),
    url(r'^(?P<year>\d{4})/$',
        entries_queryset_view_to_app(django.views.generic.date_based.archive_year),
        dict(
            make_object_list=True,
            date_field='publication_date',
        ),
        name='blog_year',
    ),
    url(r'^$', index_view, name='blog'),
    url(r'^ajouter/$', add_view),
    url(r'^(?P<pk>\d+)/modifier/$', update_view),
    url(r'^(?P<pk>\d+)/supprimer/$', delete_view),
    url(r'^mes-actualites/$', my_view),
    url(r'^mes-actualites/feedback/$', feedback_view),

    url(r'^feed/rss/$', RssEntries(), name='blog_rss_entries_feed'),
    url(r'^feed/rss/(?P<slug>[\w-]+)/$', RssTag(), name='blog_rss_tag_feed'),
)
