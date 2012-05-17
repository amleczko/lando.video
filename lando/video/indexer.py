# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer
from zope.annotation.interfaces import IAnnotations
from Missing import MV

from lando.video.interfaces import IVideo


@indexer(IVideo)
def file_url(object, **kw):
    """Return url to multipler video file_url"""
    store = IAnnotations(object)
    return store.get('lando.video.file_link', MV)


@indexer(IVideo)
def file_thumb(object, **kw):
    """Return url to multipler video file_thumb"""
    store = IAnnotations(object)
    return store.get('lando.video.file_thumb', MV)

