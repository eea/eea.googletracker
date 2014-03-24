from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing import z2

from Products.CMFCore.utils import getToolByName
from eea.googletracker.browser import track_download

#package imports
import eea.googletracker

class TUAOpener(track_download.UAOpener):
    def open(self, url):
        return url

class MyFixture(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        super(MyFixture, self).setUpZope(app, configurationContext)
        self.loadZCML(package=eea.googletracker)
        z2.installProduct(app, 'eea.googletracker')

    def setUpPloneSite(self, portal):
        super(MyFixture, self).setUpPloneSite(portal)
        self.applyProfile(portal, 'eea.googletracker:default')
        portal_properties = getToolByName(portal, 'portal_properties')
        portal_properties.site_properties.webstats_js = \
            ('''<script type="text/javascript"> var gaJsHost = '''
             '''(("https:" == document.location.protocol) ? '''
             '''"https://ssl." : "http://www."); document.write'''
             '''(unescape("%3Cscript src='" + gaJsHost + '''
             '''"google-analytics.com/ga.js' type='text/javascript'%3E%3C/'''
             '''script%3E")); </script> <script type="text/javascript"> '''
             '''try { var pageTracker = _gat._getTracker("UA-00000000-0"); '''
             '''pageTracker._trackPageview(); } catch(err) {}</script>''')

    def tearDownZope(self, app):
        super(MyFixture, self).tearDownZope(app)
        z2.uninstallProduct(app, 'eea.googletracker')

class EEAGTFunctionalTesting(FunctionalTesting):
    def testSetUp(self):
        super(EEAGTFunctionalTesting, self).testSetUp()
        portal = self['portal']
        wft = portal['portal_workflow']
        wft.setDefaultChain('plone_workflow')
        wft.updateRoleMappings()
        setRoles(portal, TEST_USER_ID, ['Manager'])
        import transaction; transaction.commit()
        self['browser'] = z2.Browser(self['app'])
        self['browser'].handleErrors = False
        self['browser'].addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))
        portal.REQUEST.environ['HTTP_HOST'] = 'nohost'
        portal.REQUEST.environ['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
        portal.REQUEST.environ['HTTP_X_FORWARDED_HOST'] = 'eea'
        portal.REQUEST.environ['HTTP_USER_AGENT'] = \
            ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.7 '
             '(KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7')
        portal.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = 'en-US,en;q=0.8'
        portal.REQUEST['SERVER_URL'] = portal.aq_parent.absolute_url()
        track_download.UAOpener = TUAOpener

FIXTURE = MyFixture()
FUNCTIONAL_TESTING = EEAGTFunctionalTesting(bases=(FIXTURE,), name='MyFixture:Functional')
