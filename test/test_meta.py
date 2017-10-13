from scrapetools.meta import Show


def test_Show():
    class A(Show):
        def __ini__(self, x, y):
            self.x = x
            self.y = y

    assert repr(A(2, 3)) == 'A(2, 3)'
