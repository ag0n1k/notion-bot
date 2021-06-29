# State definitions for top level conversation
SELECTING_ACTION, NOTION, CATEGORY, DESCRIBING_SELF = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))

# Different constants for this example
(
    PARENTS,
    CHILDREN,
    SELF,
    GENDER,
    MALE,
    FEMALE,
    AGE,
    NAME,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(10, 22))


CREATE, REMOVE, CONNECT = map(chr, range(22, 25))
CINEMA, LINK = map(chr, range(25, 27))

NOTION_CINEMA_TYPE = 'Cinema'
NOTION_LINK_TYPE = 'Link'
NOTION_PODCAST_TYPE = 'Podcast'
NOTION_EMPTY_TYPE = 'Empty'
NOTION_TYPES = [NOTION_CINEMA_TYPE, NOTION_LINK_TYPE, NOTION_PODCAST_TYPE]
