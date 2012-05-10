from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class LandoProxy(ViewletBase):

    def __init__(self, *args, **kwargs):
        super(LandoProxy, self).__init__(*args, **kwargs)
        self.lando_video = getMultiAdapter((self.context, self.request), name='multipler_upload')

    def render(self):
        video = self.lando_video.get_video()

        if video:
            return str(video)

        return ''
