#!/usr/bin/env python
# encoding: utf-8



from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = "coco"
urlpatterns = [
    path(r'',
         views.IndexView.as_view(),
         name='index'),
    path('archives.html',
    cache_page(
            60 * 60)(
            views.ArchivesView.as_view()),
         name='archives'),

    path('location.html',
        views.LocationView.as_view(),
         name='location'),
    path(
        'links.html',
        views.LinkListView.as_view(),
        name='links'),
    path(
        r'upload',
        views.fileupload,
        name='upload'),
    path(
        r'refresh',
        views.refresh_memcache,
        name='refresh'),
    path(r'locationis',
         views.locationis,
         name='locationis'),]