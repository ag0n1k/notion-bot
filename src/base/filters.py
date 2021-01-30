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