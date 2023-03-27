from mailing import constants as MAILING_CONSTANTS
from mailing import tasks, mailing_service


class MailCampaignTracker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            requestParams = request.GET.copy()
            params = {}
            if MAILING_CONSTANTS.PARAM_CAMPAIGN_KEY in requestParams:
                params[MAILING_CONSTANTS.PARAM_CAMPAIGN_KEY] = requestParams[MAILING_CONSTANTS.PARAM_CAMPAIGN_KEY]
            if MAILING_CONSTANTS.PARAM_CAMPAIGN_MEDIUM_KEY in requestParams:
                params[MAILING_CONSTANTS.PARAM_CAMPAIGN_MEDIUM_KEY] = requestParams[MAILING_CONSTANTS.PARAM_CAMPAIGN_MEDIUM_KEY]
            if params:
                mailing_service.campaign_new_visit(params)

        response = self.get_response(request)
        return response

