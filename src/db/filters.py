from base.constants import *


def empty_property(prop):
    return {
        "filters": [{
            "filter": {
                "operator": "is_empty"
            },
            "property": "{}".format(prop)
        }],
        "operator": "and"
    }


def category_todo(category):
    return {
        "filters": [{
            "property": "{}".format(CATEGORY_PROPERTY),
            "filter": {
                "operator": "enum_is",
                "value": {
                    "type": "exact",
                    "value": category
                },
            },
        },
        {
            "property": "{}".format(CATEGORY_STATUS),
            "filter": {
                "operator": "enum_is",
                "value": {
                    "type": "exact",
                    "value": "{}".format(STATUS_TODO)
                }
            }
        }],
        "operator": "and"
    }
