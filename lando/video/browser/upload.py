# -*- coding: utf-8 -*-

import urllib2
import socket
import Cookie

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from Products.Five.browser import BrowserView

from lando.video.interfaces import IMultiplerSettings


LANDO_PROXY_SESSION = 'session'
PLONE_PROXY_SESSION = 'lando.proxy.session'


class VideoUpload(BrowserView):

    @property
    def multipler_settings(self):
        """Return multipler related settings from plone.app.registry"""
        registry = queryUtility(IRegistry)
        return registry.forInterface(IMultiplerSettings, check=False)

    def get_form_url(self):
        session, token = self.get_token()
        settings = self.multipler_settings

        if session:
            print 'settings session %s' % session
            return "%s/%s/upload?set_session=%s" % (settings.lando_url, token, session)
        else:
            return "%s/%s/upload" % (settings.lando_url, token)

    def get_token(self):
        settings = self.multipler_settings
        sdm = self.context.session_data_manager

        dt = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        opener = urllib2.build_opener()

        session = sdm.getSessionData(create=True)
        plone_session = session.get(PLONE_PROXY_SESSION)
        if plone_session:
            opener.addheaders.append(('Cookie', '%s=%s' % (LANDO_PROXY_SESSION, plone_session)))

        req = opener.open('%s/get_token?token_pass=%s' % (settings.lando_url, settings.lando_pass))
        socket.setdefaulttimeout(dt)
        token = req.read()

        #trying to update plone session with pyramid session id
        cookie = Cookie.SimpleCookie()
        cookie.load(req.headers.get('Set-Cookie',''))
        try:
            proxy_session = cookie[LANDO_PROXY_SESSION].value
            session.set(PLONE_PROXY_SESSION, proxy_session)
        except KeyError:
            proxy_session = None

        return proxy_session, token
