# -*- coding: utf-8 -*-

import urllib2
import socket
import simplejson as json

from Products.Five.browser import BrowserView
from zope.component import queryUtility
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry

from lando.video.interfaces import IMultiplerSettings


PLONE_PROXY_SESSION = 'lando.proxy.session'
TIMEOUT = 3


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
        socket.setdefaulttimeout(TIMEOUT)
        req = urllib2.urlopen('%s/get_token?token_pass=%s' % (settings.lando_url, settings.lando_pass))
        socket.setdefaulttimeout(dt)
        token = req.read()

        session.set(PLONE_PROXY_SESSION, token)

        return token

    def get_video(self):
        store = IAnnotations(self.context)
        task_id = store.get('lando.video.task_id')
        file_id = store.get('lando.video.file_id')

        if task_id and not file_id:

            token = self.get_token()
            settings = self.multipler_settings

            dt = socket.getdefaulttimeout()
            socket.setdefaulttimeout(TIMEOUT)
            req = urllib2.urlopen('%s/%s/get_task/%s' % (settings.lando_url, token, task_id))
            socket.setdefaulttimeout(dt)
            result = json.loads(req.read())

            if result['admit_task'].get('result'):
                file_id = result['admit_task'].get('result').get('file_id')
                store['lando.video.file_id'] = file_id
            else:
                return result

        if file_id:
            token = self.get_token()
            settings = self.multipler_settings

            dt = socket.getdefaulttimeout()
            socket.setdefaulttimeout(TIMEOUT)
            req = urllib2.urlopen('%s/%s/video/%s/view' % (settings.lando_url, token, file_id))
            socket.setdefaulttimeout(dt)
            video = json.loads(req.read())
            return video


    def set_task_id(self, task_id=None):
        """ set celery task_id for later usage"""
        store = IAnnotations(self.context)
        taskid = task_id or json.loads(self.request.form.get('taskid'))
        store['lando.video.task_id'] = taskid
        store['lando.video.file_id'] = None #setting the task should clean file
        return 'OK'

    def set_file_id(self, file_id=None):
        """ set celery task_id for later usage"""
        store = IAnnotations(self.context)
        fileid = file_id or json.loads(self.request.form.get('fileid'))
        store['lando.video.file_id'] = fileid
        return 'OK'
