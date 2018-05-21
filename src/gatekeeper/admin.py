# -*- coding: utf-8 -*-

import transaction
import sqlalchemy as sa

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from zope.interface import Interface, implementer
from zope.location import Location
from zope.schema import Int, Choice, Text, Datetime
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from cromlech.dawnlight import traversable
from cromlech.sqlalchemy import SQLAlchemySession
from cromlech.sqlalchemy import get_session
from cromlech.webob import Response, Request
from dolmen.forms.base import Action, Actions, Fields
from cromlech.location import get_absolute_url
from dolmen.sqlcontainer import SQLContainer


Messages = declarative_base()


ALERT = u"alert"
INFO = u"infos"
ADVERT = u"advert"

ON_DATES = u"on_dates"
DISABLED = u"disabled"
ENABLED = u"enabled"


MODES = SimpleVocabulary((
    SimpleTerm(title="Always", value=ENABLED),
    SimpleTerm(title="Time span", value=ON_DATES),
    SimpleTerm(title="Disabled", value=DISABLED),
    ))


TYPES = SimpleVocabulary((
    SimpleTerm(title=u"Alert", value=ALERT),
    SimpleTerm(title=u"Information", value=INFO),
    SimpleTerm(title=u"Advertisement", value=ADVERT),
    ))


class IMessage(Interface):

    id = Int(
        title=u"Unique identifier",
        readonly=True,
        required=True)
    
    message = Text(
        title=u"Message",
        required=True)
    
    type = Choice(
        title=u"Type of message",
        vocabulary=TYPES,
        default=INFO,
        required=True)

    activation = Choice(
        title=u"Type of message",
        vocabulary=MODES,
        default=ON_DATES,
        required=True)

    enable = Datetime(
        title=u"Date of activation",
        description=u"Set empty for an immediate activation",
        required=False)

    disable = Datetime(
        title=u"Date of de-activation",
        description=u"Set empty for an immediate de-activation",
        required=False)


class Message(Location, Messages):

    __tablename__ = 'messages'

    id = sa.Column(
        'id', sa.Integer, primary_key=True)
    message = sa.Column(
        'message', sa.Text, nullable=False)
    type = sa.Column(
        'type', sa.String(32), nullable=False)
    activation = sa.Column(
        'activation', sa.String(32), nullable=False)
    enable = sa.Column(
        'enable', sa.DateTime, nullable=False, default=datetime.now())
    disable = sa.Column(
        'disable', sa.DateTime, nullable=False, default=datetime.now())


@implementer(IPublicationRoot)
class MessagesRoot(SQLContainer):
    factory = model = Message


def get_valid_messages(session):
    now = datetime.now()
    enabled = session.query(Message).filter(Message.activation == ENABLED)
    valid = session.query(Message).filter(
        Message.activation == ON_DATES).filter(
        Message.enable <= now).filter(Message.disable >= now)
    return iter(enabled.union(valid))


def messager(engine):

    publisher = DawnlightPublisher(view_lookup=view_lookup)
    
    def app(environ, start_response):
        request = Request(environ)
        with transaction.manager as tm:
            with SQLAlchemySession(engine, transaction_manager=tm) as sess:
                root = MessagesRoot(lambda: sess)
                response = publisher.publish(
                    request, root, handle_errors=True)
                result = response(environ, start_response)
        return result

