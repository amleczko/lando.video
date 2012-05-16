# -*- coding: utf-8 -*-

import urllib2, urllib
import socket
import simplejson as json

from DateTime import DateTime
from Products.Five.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry

from lando.video.interfaces import IMultiplerSettings


PLONE_PROXY_SESSION = 'lando.proxy.session'
TIMEOUT = 3

#Multipler states
UNKNOWN = -2
ERROR = -1
NONE = 0
UPLOADING = 1
UPLOADED = 2
CONVERTING = 3
READY = 4


class MultiplerAPI(BrowserView, object):
    """Main class to communicate with lando.proxy."""

    def __init__(self, *args, **kwargs):
        super(MultiplerAPI, self).__init__(*args, **kwargs)
        self.store = IAnnotations(self.context)
        self.token = self.get_token()

    @property
    def multipler_settings(self):
        """Return multipler related settings from plone.app.registry"""
        registry = queryUtility(IRegistry)
        return registry.forInterface(IMultiplerSettings, check=False)

    def get_multipler_state(self):
        """Return multipler state (for video or celery task) from annotation."""
        if 'lando.video.state' not in self.store.keys():
            self.store['lando.video.state'] = NONE
        return self.store['lando.video.state']

    def set_multipler_state(self, response):
        """Set multipler state from lando.proxy response."""
        current_state = self.multipler_state

        if not isinstance(response, dict):
            return #skip wrong responses

        #first let's check cellery task status
        if response.get('upload_task'):
            task_state = response['upload_task']['state']
            if task_state == 'SUCCESS':
                new_state = UPLOADED
            elif task_state == 'ERROR':
                new_state = ERROR
            else:
                new_state = UPLOADING
        elif response.get('response') == 'OK':
            #something has finished, now let's check what:
            video_state = response['annotation']['file_list']['file_attributes']['file_state']
            if video_state == 'ready':
                new_state = READY
                self.store['lando.video.file_link'] = response['annotation']['file_list']['file_attributes']['file_link']
            else:
                new_state = CONVERTING
        elif response.get('response') == 'NOK':
            new_state = ERROR
        else:
            new_state = UNKNOWN

        if new_state != current_state:
            #trying to set multipler state in unified way:
            #print 'state has been changed from %s to %s' % (current_state, new_state)
            self.add_multipler_state_history(response, new_state)
            self.store['lando.video.state'] = new_state

    multipler_state = property(get_multipler_state, set_multipler_state)

    def add_multipler_state_history(self, response, new_state):
        """Add multipler state to plone history viewlet"""
        pm = self.context.portal_membership
        actor = pm.getAuthenticatedMember()
        ADD_HISTORY = False
        history = {'action': 'multipler', 'actor': {}, 'actor_home': '', 'review_state': '',
                   'actorid': actor.id,
                   'time': DateTime(),
                   'comments': '',
                   'transition_title': '',
                   'type': 'multipler'}
        if new_state == READY:
            history['transition_title'] = u'Video is ready'
            history['comments'] = u'Video url is %s' % response['annotation']['file_list']['file_attributes']['file_link']
            ADD_HISTORY = True
        elif new_state == UPLOADING:
            history['transition_title'] = u'Started video upload'
            ADD_HISTORY = True
        elif new_state == UPLOADED:
            history['transition_title'] = u'Video has been uploaded'
            ADD_HISTORY = True
        elif new_state == CONVERTING:
            history['transition_title'] = u'Video is being converted'
            ADD_HISTORY = True

        if 'lando.video.states' not in self.store.keys():
            self.store['lando.video.states'] = []
        if ADD_HISTORY:
            self.store['lando.video.states'].append(history)

    def video_ready(self):
        """Return True is video is ready to display from multipler."""
        if self.file_id:
            if not self.store.get('lando.video.file_link'):
                self.multipler_request('video/%s/view' % self.file_id)
        return self.multipler_state == READY

    @property
    def task_id(self):
        """Return celery task_id."""
        return self.store.get('lando.video.task_id')

    @property
    def file_id(self):
        """Return multipler video file_id."""
        file_id = self.store.get('lando.video.file_id')
        if not file_id and self.task_id:
            result = self.multipler_request('get_task/%s' % self.task_id)
            if result and result['admit_task'].get('result'):
                file_id = result['admit_task'].get('result').get('file_id')
                self.store['lando.video.file_id'] = file_id
        return file_id

    def set_task_id(self, task_id=None):
        """ set celery task_id for later usage"""
        taskid = task_id or json.loads(self.request.form.get('taskid'))
        self.store['lando.video.task_id'] = taskid
        self.store['lando.video.file_id'] = None #setting the task should clean file
        self.store['lando.video.file_link'] = None #setting the task should clean file_link
        return 'OK'

    def get_token(self):
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

        setattr(self, 'multipler_state', result)
        return result

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

    def get_video_url(self):
        """Return the video file_link."""
        if self.video_ready():
            return self.store['lando.video.file_link']

    def render_video(self):
        """Render video viewlet."""
        template = ViewPageTemplateFile("video_view.pt")
        return template
