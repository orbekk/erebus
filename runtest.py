# -*- coding: utf-8 -*-
import unittest
import test.erebustest

if __name__ == '__main__':
    s = test.erebustest.suite()
    unittest.TextTestRunner(verbosity=2).run(s)
