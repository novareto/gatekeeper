# -*- coding: utf-8 -*-

import datetime
import time
import base64
import auth_pubtkt
import socket

from M2Crypto import RSA, EVP
from cStringIO import StringIO

from cromlech.browser import setSession, redirect_exception_response
from cromlech.browser.exceptions import HTTPRedirect
from cromlech.browser import IView, IPublicationRoot
from cromlech.webob import Request
from grokcore.component import baseclass
from dolmen.message import send

from urllib import quote
from uvclight import FAILURE
from uvclight import Form, Actions, Action, Fields, Marker, ISuccessMarker
from dolmen.forms.base.markers import SuccessMarker
from uvclight import implementer, context, get_template
from webob.exc import HTTPFound
from zope.component import getMultiAdapter, getUtilitiesFor
from zope.interface import Interface
from zope.location import Location
from zope.schema import TextLine, Password
from cromlech.sqlalchemy import create_engine, SQLAlchemySession
from .admin import get_valid_messages, Admin
from . import SESSION_KEY
from .portals import IPortal


timeout_template = get_template('timeout.pt', __file__)
unauthorized_template = get_template('unauthorized.pt', __file__)


class ILoginForm(Interface):
    """A simple login form interface.
    """
    login = TextLine(
        title=u"Username",
        required=True,
    )

    password = Password(
        title=u"Password",
        required=True,
    )


class IResponseSuccessMarker(ISuccessMarker):
    pass


@implementer(IResponseSuccessMarker)
class ResponseSuccessMarker(Marker):

    def __init__(self, success, response):
        self.success = success
        self.response = response
        self.url = None

    def __nonzero__(self):
        return bool(self.success)


# IV needs to be fixed for decrypting.
# This has been generated by Souheil.
iv = '\x92W$\xa8D\x86_O\x05#|\xda\xc2\xf4\xc1W'
PAD = '\0'


def bauth(val):
    def encrypt(data, key):
        # Zero padding
        if len(data) % 16 != 0:
            data += PAD * (16 - len(data) % 16)
            buffer = StringIO()
            cipher = EVP.Cipher('aes_128_cbc', key=key, iv=iv, op=1)
            cipher.set_padding(0)
            buffer.write(cipher.update(str(data)))
            buffer.write(cipher.final())
            data = iv + buffer.getvalue()
        return data
    return encrypt(val, 'mKaqGWwAVNnthL6J')


def read_bauth(val):
    # Return the decryption function
    def decrypt(data, key):
        data = base64.b64decode(data)
        data = data.lstrip(iv)
        cipher = EVP.Cipher('aes_128_cbc', key=key, iv=iv, op=0)
        cipher.set_padding(0)
        v = cipher.update(str(data))
        v = v + cipher.final()
        del cipher
        return v
    return decrypt(val, 'mKaqGWwAVNnthL6J')


@implementer(IPublicationRoot)
class BaseRoot(Location):
    """ """

@implementer(IPublicationRoot)
class LoginRoot(Location):

    def __init__(self, pkey, dest, dburl, dbkey):
        self.pkey = pkey
        self.dest = dest
        self.dbkey = dbkey
        self.engine = create_engine(dburl, dbkey)
        self.engine.bind(Admin)

    def get_base_messages(self):
        messages = []
        with SQLAlchemySession(self.engine) as session:
            messages = get_valid_messages(session)
        return messages

    def get_messages(self):
        return [m.message for m in self.get_base_messages()]


class LogMe(Action):

    def available(self, form):
        return True

    def cook(self, form, login, password, authenticated_for, back='/'):
        privkey = RSA.load_key(form.context.pkey)
        val = base64.encodestring(bauth('%s:%s' % (login, password)))
        validtime = datetime.datetime.now() + datetime.timedelta(hours=1)
        validuntil = int(time.mktime(validtime.timetuple()))
        ticket = auth_pubtkt.create_ticket(
            privkey, login, validuntil, tokens=list(authenticated_for),
            extra_fields=(('bauth', val),))

        res = HTTPFound(location=back)
        res.set_cookie('auth_pubtkt', quote(ticket), path='/',
                       domain='novareto.de', secure=False)
        return res

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.submissionError = errors
            return FAILURE

        login = data.get('login')
        password = data.get('password')

        authenticated_for = form.authenticate(login, password)
        if authenticated_for:
            sent = send(u'Login successful.')
            assert sent is True
            res = self.cook(
                form, login, password, authenticated_for, form.context.dest)
            return ResponseSuccessMarker(True, res)
        else:
            sent = send(u'Login failed.')
            assert sent is True
            url = form.request.url
            return SuccessMarker('LoginFailed', False, url=url)


class BaseLoginForm(Form):
    baseclass()
    context(LoginRoot)

    fields = Fields(ILoginForm)
    actions = Actions(LogMe(u'Authenticated'))

    def available(self):
        marker = True
        for message in self.context.get_base_messages():
            if message.type == "alert":
                marker = False
        return marker

    def authenticate(self, login, password):
        gates = getUtilitiesFor(IPortal)
        authenticated_for = set()
        for name, gate in gates:
            try:
                if gate.check_authentication(login, password):
                    authenticated_for.add(name)
            except socket.error:
                print "%r could not be resolved" % name
        return authenticated_for

    def updateForm(self):
        if self._updated is False:
            action, result = self.updateActions()
            if IResponseSuccessMarker.providedBy(result):
                return result.response
            self.updateWidgets()
            self._updated = True
        return None

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            response = self.updateForm()
            if response is None:
                result = self.render(*args, **kwargs)
                response = self.make_response(result, *args, **kwargs)
            return response
        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)


def login(global_conf, pkey, dest, dburl, dbkey, **kwargs):
    root = LoginRoot(pkey, dest, dburl, dbkey)

    def app(environ, start_response):
        session = environ[SESSION_KEY].session
        setSession(session)
        request = Request(environ)
        form = getMultiAdapter((root, request), Interface, u'loginform')
        response = form()(environ, start_response)
        setSession()
        return response
    return app


def timeout(global_conf, **kwargs):
    root = BaseRoot()

    def app(environ, start_response):
        request = Request(environ)
        view = getMultiAdapter((root, request), IView, name="timeout")
        response = view()
        return response(environ, start_response)
    return app


def unauthorized(global_conf, **kwargs):
    root = BaseRoot()

    def app(environ, start_response):
        request = Request(environ)
        view = getMultiAdapter((root, request), IView, name="unauthorized")
        response = view()
        return response(environ, start_response)
    return app