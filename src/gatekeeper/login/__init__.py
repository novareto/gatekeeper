# -*- coding: utf-8 -*-

from cromlech.webob import Request
from cromlech.browser import PublicationBeginsEvent, PublicationEndsEvent
from zope.interface import alsoProvides
from zope.event import notify
#from .models import LoginRoot


def login(global_conf, pkey, dest, dburl, dbkey, layer, session_key, **kwargs):
    root = LoginRoot(pkey, dest, dburl, dbkey)

    def app(environ, start_response):
        setLanguage('de')
        session = environ[session_key].session
        setSession(session)
        request = Request(environ)
        skin_layer = eval_loader(layer)
        alsoProvides(request, skin_layer)
        notify(PublicationBeginsEvent(root, request))
        form = query_view(request, root, name=u'loginform')
        response = form()(environ, start_response)
        notify(PublicationEndsEvent(root, request, response))
        setSession()
        return response
    return app


def timeout(global_conf, layer, **kwargs):
    def app(environ, start_response):
        setLanguage('de')
        request = Request(environ)
        skin_layer = eval_loader(layer)
        alsoProvides(request, skin_layer)
        view = query_view(request, environ, name="timeout")
        response = view()
        return response(environ, start_response)
    return app


def unauthorized(global_conf, layer, **kwargs):
    def app(environ, start_response):
        setLanguage('de')
        request = Request(environ)
        skin_layer = eval_loader(layer)
        alsoProvides(request, skin_layer)
        view = query_view(request, environ, name="unauthorized")
        response = view()
        return response(environ, start_response)
    return app
