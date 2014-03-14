import logging

SESSION_KEY = "gatekeeper.session"
logger = logging.getLogger('gatekeeper')


def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)
