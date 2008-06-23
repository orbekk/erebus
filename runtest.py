import unittest
import test.item_test

if __name__ == '__main__':
    s = test.item_test.suite()
    unittest.TextTestRunner(verbosity=2).run(s)
