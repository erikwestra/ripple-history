""" rippleHistory.urls

    This module defines the top-level URLs for the rippleHistory system.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('rippleHistory.api.views',
    url(r'^lookup/(?P<ripple_address>(.+))/$', 'lookup'),
    url(r'^get/(?P<ripple_address>(.+))/$',    'get'),
    url(r'^balances/$',                        'balances'),
)
