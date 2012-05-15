# -*- coding: utf-8 -*-

import urllib2, urllib
import socket
import simplejson as json

from Products.Five.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry

from lando.video.interfaces import IMultiplerSettings


PLONE_PROXY_SESSION = 'lando.proxy.session'
TIMEOUT = 3


class MultiplerAPI(BrowserView):

    def __init__(self, *args, **kwargs):
        super(MultiplerAPI, self).__init__(*args, **kwargs)
        self.store = IAnnotations(self.context)
        self.task_id = self.store.get('lando.video.task_id')
        self.file_id = self.store.get('lando.video.file_id')
        self.token = self._get_token()
        self._try_to_get_file_id_()

    def _try_to_get_file_id_(self):
        if not self.task_id and self.file_id:
            return

        result = self.multipler_request('get_task/%s' % self.task_id)
        if result and result['admit_task'].get('result'):
            file_id = result['admit_task'].get('result').get('file_id')
            self.store['lando.video.file_id'] = file_id

    def _get_token(self):
        """Return two valued token from lando.proxy"""
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        token = session.get(PLONE_PROXY_SESSION, None)
        if token:
            return token

        settings = self.multipler_settings

        dt = socket.getdefaulttimeout()
        socket.setdefaulttimeout(TIMEOUT)
        try:
            req = urllib2.urlopen('%s/get_token?token_pass=%s' % (settings.lando_url, settings.lando_pass))
        except (socket.timeout, urllib2.URLError):
            socket.setdefaulttimeout(dt)
            return
        socket.setdefaulttimeout(dt)
        token = req.read()
        session.set(PLONE_PROXY_SESSION, token)
        return token

    def multipler_request(self, path):
        """Unified lando.proxy requests"""
        settings = self.multipler_settings

        dt = socket.getdefaulttimeout()
        socket.setdefaulttimeout(TIMEOUT)
        try:
            req = urllib2.urlopen('%s/%s/%s' % (settings.lando_url, self.token, path))
        except (socket.timeout, urllib2.URLError):
            socket.setdefaulttimeout(dt)
            return

        socket.setdefaulttimeout(dt)
        result = json.loads(req.read())

        return result

    @property
    def multipler_settings(self):
        """Return multipler related settings from plone.app.registry"""
        registry = queryUtility(IRegistry)
        return registry.forInterface(IMultiplerSettings, check=False)

    def form_url(self):
        """Return form url for ajax calls"""
        if not self.token:
            return

        settings = self.multipler_settings
        params = {}

        title = self.context.title_or_id()
        if title:
            params['title'] = title

        description = self.context.Description()
        if description:
            params['description'] = description

        query = urllib.urlencode(params)

        return "%s/%s/upload?%s" % (settings.lando_url, self.token, query)

    def set_task_id(self, task_id=None):
        """ set celery task_id for later usage"""
        taskid = task_id or json.loads(self.request.form.get('taskid'))
        self.store['lando.video.task_id'] = taskid
        self.store['lando.video.file_id'] = None #setting the task should clean file
        return 'OK'

    def get_video(self):
        "return the video json response"""
        if self.file_id:
            response = self.multipler_request('video/%s/view' % self.file_id)
            if response.get('response', 'NOK') == 'OK':
                return response

    def get_task_status(self):
        "return json celery task information"
        if self.task_id:
            return self.multipler_request('get_task/%s' % self.task_id)

    def render_video(self):
        template = ViewPageTemplateFile("video_view.pt")
        return template
