class NBotCategory(object):
    def __init__(self):
        self._name = None
        self._domains = []

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
