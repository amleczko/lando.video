from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class LandoProxy(ViewletBase):

    def __init__(self, *args, **kwargs):
        super(LandoProxy, self).__init__(*args, **kwargs)
        self.lando = getMultiAdapter((self.context, self.request), name='multipler_upload')

    def render(self):
        template = self.lando.render_video()
        return template(self.lando)
