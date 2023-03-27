MAX_RECENT = 5
TOP_VIEWS_MAX = 10
PAGINATED_BY = 30
PAGINATION_MAX_SIZE = 50
SHORT_DESCRIPTION_MAX_SIZE = 164
DESCRIPTION_MAX_SIZE = 300

SETTINGS_BASE_TEMPLATE_INHERIT = "MAILING_BASE_TEMPLATE_INHERIT"
SETTINGS_TEMPLATE_CAMPAIGNS_PAGE = "MAILING_CAMPAIGNS_PAGE"
SETTINGS_TEMPLATE_CAMPAIGN_PAGE  = "MAILING_CAMPAIGN_PAGE"
SETTINGS_TEMPLATE_CAMPAIGN_CREATE_PAGE = "MAILING_CAMPAIGN_CREATE_PAGE"
SETTINGS_TEMPLATE_CAMPAIGN_UPDATE_PAGE = "MAILING_CAMPAIGN_UPDATE_PAGE"
SETTINGS_DEFAULT_MAIL_TEMPLATE = "MAILING_DEFAULT_MAIL_TEMPLATE"
SETTINGS_SEND_ONLY_TO_VERIFIED_USERS = "MAILING_SEND_ONLY_TO_VERIFIED_USERS"
SETTINGS_MAILING_TEMPLATE_CONTEXTS = "MAILING_TEMPLATE_CONTEXTS"
SETTINGS_MAILING_TEMPLATE_CONTEXTS_KEYS = "MAILING_TEMPLATE_CONTEXTS_KEY"
DEFAULT_SEND_ONLY_TO_VERIFIED_USERS = True
DEFAULT_MAILING_CAMPAIGNS_PAGE = "mailing/campaigns.html"
DEFAULT_MAILING_CAMPAIGN_PAGE = "mailing/campaign.html"
DEFAULT_MAILING_CAMPAIGN_CREATE_PAGE ="mailing/campaign_create.html"
DEFAULT_MAILING_CAMPAIGN_UPDATE_PAGE ="mailing/campaign_update.html"

REQUIRED_SETTINGS = [
    SETTINGS_BASE_TEMPLATE_INHERIT, SETTINGS_DEFAULT_MAIL_TEMPLATE, SETTINGS_MAILING_TEMPLATE_CONTEXTS, SETTINGS_MAILING_TEMPLATE_CONTEXTS_KEYS
]


PARAM_CAMPAIGN_MEDIUM_KEY = "email"
PARAM_CAMPAIGN_KEY = "campaign"
