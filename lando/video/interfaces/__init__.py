# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from video import IVideo; IVideo
from lando.video import videoMessageFactory as _


class IMultiplerSettings(Interface):
    """Settings used by the mutlipler upload form.
    Should be installed into ``plone.registry``.
    """

    lando_url = schema.URI(
                    title=_(u"Connection url to lando.proxy"),
                    required=True,
                    default='http://localhost:6543',
                    missing_value='http://localhost:6543',
                    description=_('help_lando_url',
                        default=u"This should be the proper URL to proxy application, something like: "
                                u"http://landoproxy.redturtle.it/")
            )

    lando_pass = schema.Password(
                    title=_(u"lando.proxy token pass"),
                    required=True,
                    default='s3cr3t',
                    missing_value='s3cr3t',
                    description=_('help_lando_pass',
                        default=u"This should be the proper lando.proxy pass phrase.")
            )

