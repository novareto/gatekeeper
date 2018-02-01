# -*- coding: utf-8 -*-

import logging
from os import path

from cromlech.browser import IView
from cromlech.browser.interfaces import ITypedRequest
from cromlech.i18n import Locale
from cromlech.webob import Response
from cromlech.webob.request import Request
from dolmen.template import TALTemplate
from dolmen.view import View, make_layout_response
from zope.i18nmessageid import MessageFactory
from .login.interfaces import DirectResponse


i18n = MessageFactory("gatekeeper")
logger = logging.getLogger('gatekeeper')
TEMPLATE_DIR = path.join(path.dirname(__file__), 'templates')


def tal_template(name):
    return TALTemplate(name, _prefix=TEMPLATE_DIR)


def query_view(request, obj, name=""):
    return IView(obj, request, name=name)


def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)


def serve_view(viewname, root=None, skin_layer=None):

    def app(environ, start_response):
        with Locale('de'):
            try:
                request = Request(environ)
                if skin_layer:
                    alsoProvides(request, skin_layer)
                form = query_view(request, root or environ, name=viewname)
                response = form()(environ, start_response)
            except DirectResponse as dr:
                print(dr)
                response = dr.response(environ, start_response)
        return response

    return app


class Page(View):
    responseFactory = Response
    make_response = make_layout_response


class DefaultLayer(ITypedRequest):
    pass
