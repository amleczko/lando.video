from plone.memoize.instance import memoize
from zope.annotation.interfaces import IAnnotations
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from zope.component import getMultiAdapter


class LandoProxy(ViewletBase):

    def __init__(self, *args, **kwargs):
        super(LandoProxy, self).__init__(*args, **kwargs)
        self.lando = getMultiAdapter((self.context, self.request), name='multipler_upload')

    def render(self):
        template = self.lando.render_video()
        return template(self.lando)


class LandoContentHistoryViewlet(ContentHistoryViewlet):

    def multiplerHistory(self):
        store = IAnnotations(self.context)
        history = store.get('lando.video.states',[])
        return history

    @memoize
    def fullHistory(self):
        history=self.workflowHistory(complete=True) + self.revisionHistory() + self.multiplerHistory()
        history=[entry for entry in history if entry.get("action", False)]
        history.sort(key=lambda x: x["time"], reverse=True)
        return history
