import unittest
import doctest
from plone.testing import layered
from eea.googletracker.tests import base

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(
                    'docs/tracker.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
        layered(doctest.DocFileSuite(
                    'docs/pageview.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
        layered(doctest.DocFileSuite(
                    'docs/event.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
        layered(doctest.DocFileSuite(
                    'docs/language.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
        layered(doctest.DocFileSuite(
                    'docs/ipv6.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
        layered(doctest.DocFileSuite(
                    'docs/host.txt',
                    package='eea.googletracker',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
