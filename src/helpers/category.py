import logging

logger = logging.getLogger(__name__)


class NBotCategoryContainer(object):
    def __init__(self):
        self._categories = dict()

    def __get__(self, instance, owner):
        return self._categories

    def __set__(self, instance, value):
        for k, v in value.items():
            self._categories.update({k: NBotCategory(name=k, domains=v)})

    def __add__(self, name):
        if not self._categories.get(name, None):
            self._categories.update({name: NBotCategory(name=name)})

    def __repr__(self):
        return [str(i) for i in self._categories.values()]

    def __delitem__(self, key):
        if self._categories.get(key, None):
            del self._categories[key]

    def __getitem__(self, domain):
        for name, cat in self._categories.items():
            if cat.search(domain):
                logger.info("Category was found: {cat}".format(cat=cat.name))
                return cat
            logger.info("No category was found")
            return None

    def update(self, category, domain):
        cat = self._categories.get(category, None)
        if not cat:
            logger.info("Category not found")
            self.add_category(category)
            self.update(category, domain)
        else:
            cat += domain
            self.save_categories()


    @property
    def names(self):
        return [i for i in self._categories.keys()]


class NBotCategory(object):
    def __init__(self, name=None, domains=()):
        self._name = name
        self._domains = list(domains)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        return self._domains

    @domains.setter
    def domains(self, value):
        self._domains = value

    def __add__(self, other):
        if not isinstance(other, list):
            other = [other]
        self._domains.extend(list(set(other).difference(set(self.domains))))

    def search(self, domain: str):
        return self._name if domain in self._domains else None

    def __str__(self):
        return "{}: {}".format(self._name, self.domains)

    @property
    def dump(self):
        return {
            'name': self._name,
            'domains': self._domains
        }


