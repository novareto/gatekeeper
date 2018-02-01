# -*- coding: utf-8 -*-

from os import path
from zope.interface import Interface
from zope.schema import TextLine, Password
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("gatekeeper")


class ILoginForm(Interface):
    """A simple login form interface.
    """
    login = TextLine(
        title=_(u"Username", default=u"Username"),
        required=True,
    )

    password = Password(
        title=_(u"Password", default=u"Password"),
        required=True,
    )

    back = TextLine(
        title=u"back",
        required=False,
    )


class DirectResponse(Exception):

    def __init__(self, response):
        self.response = response
