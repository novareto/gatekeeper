# -*- coding: utf-8 -*-

from cromlech.browser import IPublicationRoot
from zope.interface import implementer
from zope.location import Location


@implementer(IPublicationRoot)
class LoginRoot(Location):

    def get_messages(self, environ):
        return [{'msg': m.message, 'type': m.type}
                for m in environ.get('messages', [])]
