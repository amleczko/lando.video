# -*- coding: utf-8 -*-

import urllib2
import socket

from Products.Five.browser import BrowserView
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from lando.video.interfaces import IMultiplerSettings


PLONE_PROXY_SESSION = 'lando.proxy.session'


class VideoUpload(BrowserView):

    @property
    def multipler_settings(self):
        """Return multipler related settings from plone.app.registry"""
        registry = queryUtility(IRegistry)
        return registry.forInterface(IMultiplerSettings, check=False)

    def get_form_url(self):
        token = self.get_token()
        settings = self.multipler_settings
        return "%s/%s/upload" % (settings.lando_url, token)

    def get_token(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        token = session.get(PLONE_PROXY_SESSION, None)
        if token:
            return token

        settings = self.multipler_settings

        dt = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        opener = urllib2.build_opener()

        req = opener.open('%s/get_token?token_pass=%s' % (settings.lando_url, settings.lando_pass))
        socket.setdefaulttimeout(dt)
        token = req.read()
        session.set(PLONE_PROXY_SESSION, token)

        return token
