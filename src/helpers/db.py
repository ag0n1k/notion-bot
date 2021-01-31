from random import randint

from base.constants import *
from db.filters import category_todo


def get_statuses(cv):
    res = set()
    for i in cv.collection.get_rows():
        if i.status:
            res.add(i.status)
        else:
            i.status = STATUS_TODO
    return list(res)


def get_all_categories_domains(cv):
    res = {}
    res_ = []
    for i in cv.collection.get_rows():
        cur = res.get(i.category, None)
        if not cur:
            cur = set()
        cur.add(i.domain)
        res.update({i.category: cur})
    for k, v in res.items():
        res_.append("{}: {}".format(k, list(v)))
    return "\n".join(res_)


def get_rand(cv, category):
    query = cv.build_query(filter=category_todo(category)).execute()
    return query[randint(0, len(query) - 1)].get_browseable_url()
