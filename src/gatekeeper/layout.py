# -*- coding: utf-8 -*-

import crom
from dolmen.message import receive
from zope.interface import Interface
from dolmen.viewlet import ViewletManager, viewlet_manager
from cromlech.i18n import getLocale
from cromlech.webob import Response
from cromlech.browser import IRequest, ILayout
from . import DefaultLayer, tal_template


@viewlet_manager
class Top(ViewletManager):
    pass


@viewlet_manager
class Footer(ViewletManager):
    pass


class Layout(object):

    title = "Gatekeeper"
    template = tal_template('layout.pt')
    responseFactory = Response
    resources = []
    
    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.target_language = getLocale()

    def namespace(self, **extra):
        namespace = {
            'context': self.context,
            'request': self.request,
            'layout': self,
            }
        namespace.update(extra)
        return namespace

    def __call__(self, content, **namespace):
        for resource in self.resources:
            resource.need()
        environ = self.namespace(**namespace)
        environ['content'] = content
        environ['user'] = self.request.environment.get('REMOTE_USER')
        if self.template is None:
            raise NotImplementedError("Template is not defined.")
        return self.template.render(
            self, target_language=self.target_language, **environ)
