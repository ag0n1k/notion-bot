from nbot.utils import get_domain, get_omdb_id, create_buttons, MetaSingleton


def test_domain():
    assert get_domain("http://youtube.com/aw2asd/") == "youtube.com"
    assert get_domain("http://www.youtube.com/aw2asd/") == "youtube.com"


def test_positive_omdb_id():
    assert get_omdb_id("https://www.imdb.com/title/tt0993840/") == "tt0993840"
    assert get_omdb_id("https://www.imdb.com/title/tt6079772/?ref_=nv_sr_srsg_0") == "tt6079772"
    assert get_omdb_id("https://m.imdb.com/title/tt7888964/") == "tt7888964"
    assert get_omdb_id("https://m.imdb.com/title/tt1865505/?ref_=fn_al_tt_0") == "tt1865505"


def test_negative_omdb_id():
    assert get_omdb_id("https://www.imdb.com") is None
    assert get_omdb_id("https://m.imdb.com/") is None


def test_buttons():
    assert len(create_buttons([1, 2, 3])) == 2
    assert len(create_buttons([1, 2, 3], 3)) == 2
    assert len(create_buttons([1, 2, 3, 4, 5, 6])) == 3
    assert len(create_buttons([1, 2, 3, 4, 5, 6, 7, 8, 9])) == 4

    assert len(create_buttons([1, 2, 3])[0]) == 2
    assert len(create_buttons([1, 2, 3], 3)[0]) == 2
    assert len(create_buttons([1, 2, 3, 4, 5, 6])[0]) == 2
    assert len(create_buttons([1, 2, 3, 4, 5, 6, 7, 8, 9])[0]) == 2

    assert len(create_buttons([1, 2, 3, 4], 4)[0]) == 3
    assert len(create_buttons([1, 2, 3, 4, 5, 6], 4)[0]) == 3


class TestMeta(metaclass=MetaSingleton):
    def __init__(self):
        self.a = 5


def test_meta_singleton():
    a = TestMeta()
    b = TestMeta()
    assert a == b
    assert a.a == b.a
