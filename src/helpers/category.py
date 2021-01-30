import logging

logger = logging.getLogger(__name__)


class NBotCategoryContainer(object):
    def __init__(self):
        self._categories = {}

    def __get__(self, instance, owner):
        logger.info("Get _categories")
        return self._categories.values()

    def __set__(self, instance, value):
        for k, v in value.items():
            self._categories.update({k: NBotCategory(name=k, domains=v)})

    def __repr__(self):
        return "\n".join([str(i) for i in self._categories.values()])

    def __delitem__(self, key):
        if self._categories.get(key, None):
            del self._categories[key]

    def remove_domain(self, domain):
        cat = self.search(domain)
        if cat:
            logger.info("Removing '{}' from category '{}'".format(domain, cat.name))
            cat.remove(domain)

    def __getitem__(self, key):
        return self._categories.get(key, None)

    def search(self, domain):
        logger.info("Trying to get category for the domain: {}".format(domain))
        for name, cat in self._categories.items():
            if cat.search(domain):
                logger.info("Category was found: {cat}".format(cat=cat.name))
                return cat
            logger.info("No category was found")
            return None

    def dump(self):
        return [i.dump for i in self._categories.values()]

    def load(self, body: list):
        for item in body:
            cat = NBotCategory()
            cat.load(item)
            self._categories.update({cat.name: cat})

    def update(self, name):
        if not self._categories.get(name, None):
            logger.info("Adding new category: {}".format(name))
            self._categories.update({name: NBotCategory(name=name)})

    @property
    def names(self):
        return [i for i in self._categories.keys()]

    @property
    def domains(self):
        res = []
        for i in self._categories.values():
            res.extend(i.domains)
        return sorted(res)


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

    def remove(self, domain):
        logger.info("Removing {} from {}".format(domain, self._domains))
        self._domains.remove(domain)

    def __add__(self, other):
        if not isinstance(other, list):
            other = [other]
        self._domains.extend(list(set(other).difference(set(self.domains))))

    def update(self, other):
        logger.info("Updating domains {} with: {}".format(self.domains, other))
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

    def load(self, body):
        self.name = body['name']
        self.domains = body['domains']
