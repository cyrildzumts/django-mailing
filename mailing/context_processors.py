from django.template import RequestContext
import logging

logger = logging.getLogger(__name__)


def mailing_context(request):
    context = {'mailing-version': '1.0.0'}
    return context