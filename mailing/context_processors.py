from django.template import RequestContext
import logging

logger = logging.getLogger(__name__)


def mailing_context(request):
    context = {}
    requestContext = RequestContext(request)
    logger.info(f"mailing_context : {requestContext.dicts}")
    return context