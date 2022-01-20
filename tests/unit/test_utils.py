from nbot.utils import domain, MetaSingleton


def test_domain():
    assert domain("http://youtube.com/aw2asd/") == "youtube.com"
    assert domain("http://www.youtube.com/aw2asd/") == "youtube.com"


class TestMeta(metaclass=MetaSingleton):
    def __init__(self):
        self.a = 5


def test_meta_singleton():
    a = TestMeta()
    b = TestMeta()
    assert a == b
    assert a.a == b.a
