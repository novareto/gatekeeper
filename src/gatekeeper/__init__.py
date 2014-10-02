import logging
from zope.i18nmessageid import MessageFactory

SESSION_KEY = "gatekeeper.session"
i18n = MessageFactory("gatekeeper")

logger = logging.getLogger('gatekeeper')

def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)
