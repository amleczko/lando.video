# -*- coding: utf-8 -*-

"""Definition of the Video content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from zope.component import getMultiAdapter

# -*- Message Factory Imported Here -*-

from lando.video.interfaces import IVideo
from lando.video.config import PROJECTNAME

VideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

VideoSchema['title'].storage = atapi.AnnotationStorage()
VideoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VideoSchema, moveDiscussion=False)


class Video(base.ATCTContent):
    """Multipler Video"""
    implements(IVideo)

    meta_type = "MultiplerVideo"
    schema = VideoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Video, PROJECTNAME)


def videoModified(video, event):
    lando = getMultiAdapter((video, video.REQUEST), name='multipler_upload')
    if lando.video_ready():
        lando.update_video()


def videoRemoved(video, event):
    """Thank you plone.app.integrity for this stupid code. """
    lando = getMultiAdapter((video, video.REQUEST), name='multipler_upload')
    DELETE = False
    if video.REQUEST.get('URL').endswith('folder_delete'):
        DELETE = True
    elif video.REQUEST.get('HTTP_REFERER') == video.REQUEST.get('URL')\
         and video.REQUEST.get('URL').endswith('delete_confirmation'):
        DELETE = True
    if DELETE:
        if lando.video_ready():
            lando.delete_video()
