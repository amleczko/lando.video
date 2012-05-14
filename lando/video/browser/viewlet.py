import socket
import urllib2
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class LandoProxy(ViewletBase):

    def __init__(self, *args, **kwargs):
        super(LandoProxy, self).__init__(*args, **kwargs)
        self.lando_video = getMultiAdapter((self.context, self.request), name='multipler_upload')

    def render(self):
        try:
            video = self.lando_video.get_video()
        except (socket.timeout, urllib2.URLError), exc:
                return exc
        if video:
            return str(video)
        else:
            return ''
