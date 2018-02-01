# -*- coding: utf-8 -*-

import datetime
import time
import base64
import socket

from cromlech.browser import redirect_exception_response
from cromlech.browser.exceptions import HTTPRedirect

from dolmen.forms.base.markers import HIDDEN
from dolmen.forms.base import FAILURE, SuccessMarker
from dolmen.forms.base import Form, Actions, Action, Fields
from dolmen.message import send

from gatekeeper import ticket as tlib
from urllib.parse import quote
from webob.exc import HTTPFound
from zope.i18nmessageid import MessageFactory

from .models import LoginRoot
from .interfaces import ILoginForm, DirectResponse
import logging

log = logging.getLogger()


_ = MessageFactory("gatekeeper")


class LogMe(Action):

    def available(self, form):
        return True

    def cook(self, form, login, password, authenticated_for, back):
        privkey = tlib.read_key(form.context.pkey)
        cipher = form.request.environment['aes_cipher']
        val = base64.b64encode(
            tlib.bauth(
                cipher,
                '%s:%s' % (login, password))
        )
        #val = val.replace('\n', '', 1)
        validtime = datetime.datetime.now() + datetime.timedelta(hours=1)
        validuntil = int(time.mktime(validtime.timetuple()))
        ticket = tlib.create_ticket(
            privkey, login, validuntil, tokens=list(authenticated_for),
            extra_fields=(('bauth', val),))

        back = form.back(login)
        #log.debug(back)
        print ("BACK BACK BACK %s" %back)
        res = HTTPFound(location=back)
        res.set_cookie('auth_pubtkt', quote(ticket), path='/',
                       domain='kuvb.de', secure=True)
        return res

    def __call__(self, form):
        print ("START CALL")
        data, errors = form.extractData()
        print (data)
        print(errors)

        if errors:
            form.submissionError = errors
            return FAILURE

        login = data.get('login')
        password = data.get('password')

        authenticated_for = form.authenticate(login, password)
        print ("JAJAJAJAJAJ")
        if authenticated_for:
            send(_(u'Login successful.'))
            res = self.cook(
                form, login, password, authenticated_for, form.context.dest)
            raise DirectResponse(res)
        else:
            sent = send(_(u'Login failed.'))
            assert sent is True
            url = form.request.url
            return SuccessMarker('LoginFailed', False, url=url)



class BaseLoginForm(Form):

    prefix = ""
    fields = Fields(ILoginForm).omit('back')
    #fields['back'].mode = HIDDEN
    #fields['back'].prefix = ""
    actions = Actions(LogMe(_(u'Authenticate')))
    ignoreRequest = False

    def back(self, login):
        return self.context.dest

    def available(self):
        marker = True
        for message in self.context.get_base_messages():
            if message.type == "alert":
                marker = False
        return marker

    def authenticate(self, login, password):
        raise NotImplementedError('Implement your own.')
