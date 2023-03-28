from django import template
from mailing import constants as MAILING_CONSTANTS

register = template.Library()

def find_element_by_key_in_tuples(key, tuples):
    value = None
    for k, v in tuples:
        if k == key:
            value = v
            break
    return key, value


@register.filter
def published_status_value(key):
    k,v = find_element_by_key_in_tuples(key, MAILING_CONSTANTS.PUBLISHED_STATUS)
    if v is None:
        return key
    
    return v