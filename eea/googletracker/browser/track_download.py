from urllib import quote
from urllib import FancyURLopener
from time import time
from random import randint

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger("eea.googletracker")
import traceback


def _log(fname, url='no-url'):
    try:
        error = traceback.format_exc().split('\n')[-2]
        logger.info('%s: %s encountered for %s' % (fname, error, url))
    except:
        pass

class UAOpener(FancyURLopener):
    def set_user_agent(self, context):
        try:
            user_agent = context.REQUEST.environ['HTTP_USER_AGENT']
            self.addheaders = [('User-Agent', user_agent)]
        except:
            _log('set_user_agent')

class TrackDownload(BrowserView):
    def __call__(self, obj, field):
        opener = self.get_opener()
        if self.get_event_category(obj) != 'Image':
            self.trackPageview(obj, opener)
        self.trackEvent(obj, opener)

    def get_opener(self):
        url_opener = UAOpener()
        url_opener.set_user_agent(self.context)
        return url_opener

    def trackPageview(self, obj, opener):
        gif_params = self.base_gif_params(obj)
        ga_url = self.build_ga_link(gif_params)
        opener.open(ga_url)
        return ga_url

    def trackEvent(self, obj, opener):
        category = self.get_event_category(obj)
        gif_params = self.base_gif_params(obj)
        gif_params.extend(self.event_gif_params(category))
        ga_url = self.build_ga_link(gif_params)
        opener.open(ga_url)
        return ga_url

    def get_event_category(self, obj):
        try:
            return obj.portal_type
        except:
            _log('get_event_category', obj.absolute_url(1))
        return 'Undefined'

    def event_gif_params(self, category='Undefined'):
        gif_params = [
            ('utmt', 'event'),
            ('utme', '5(%s*Download*%s)' % (category, self.get_url())),
        ]
        return gif_params

    def base_gif_params(self, obj):
        # utmp must be followed by utmac
        # otherwise the wrong url will be indexed
        gif_params = [
            ('utmwv', 1),
            ('utmn', randint(1000000000, 9999999999)),
            ('utmhn', self.get_host()),
            ('utmul', self.get_user_language()),
            ('utmdt', quote(self.get_vocabulary_value(obj, 'title'))),
            ('utmr', self.context.REQUEST.get('HTTP_REFERER', '-')),
            ('utmp', self.get_url()),
            ('utmac', self.ua_to_mo(self.get_account())),
            ('utmip', self.anonymize_ip(self.get_remote_ip())),
            ('utmcc', quote(self.get_cookie())),
        ]
        return gif_params


    def build_ga_link(self, gif_params):
        if 'https' in self.context.REQUEST['SERVER_URL']:
            ga_utm = 'https://ssl.google-analytics.com/__utm.gif'
        else:
            ga_utm = 'http://www.google-analytics.com/__utm.gif'

        # urlencode will also encode the '/' in utmp
        # resulting in bad analytics results
        ga_params = '&'.join(
                ['='.join((str(k), str(v)))
                    for k, v in gif_params]
            )
        ga_link = '%s?%s' % (ga_utm, ga_params)
        return ga_link

    def get_host(self):
        environ = self.context.REQUEST.environ
        fwd_host = environ.get('HTTP_X_FORWARDED_HOST', '')
        host = environ.get('HTTP_HOST', '-')
        return quote(fwd_host or host)

    def get_user_language(self):
        try:
            environ = self.context.REQUEST.environ
            browser_languages = environ.get('HTTP_ACCEPT_LANGUAGE', '(not set)')
            languages = browser_languages.split(',')
            languages = [lang.split(';')[0] for lang in languages]
            return languages[0]
        except:
            _log('get_user_language')

    def get_vocabulary_value(self, obj, fname):
        field = obj.getField(fname)
        vocab = field.Vocabulary(obj)
        fvalue = vocab.getValue(field.get(obj))
        if not fvalue:
            return obj[fname]
        else:
            return fvalue

    def get_account(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        tracker_script = portal_properties.site_properties.webstats_js
        tracker_script = tracker_script.replace('"', "'")

        for item in tracker_script.split("'"):
            if item.startswith('UA'):
                return item

    def ua_to_mo(self, account):
        split_account = account.split('-')
        if split_account[0] == 'UA':
            split_account[0] = 'MO'
        return '-'.join(split_account)

    def get_remote_ip(self):
        try:
            return self.context.REQUEST.environ['HTTP_X_FORWARDED_FOR']
        except:
            _log('get_remote_ip')
            return '0.0.0.0'

    def anonymize_ip(self, ip):
        if '.' in ip:
            return self.anonymize_ipv4(ip)
        elif ':' in ip:
            return self.anonymize_ipv6(ip)

    def anonymize_ipv6(self, ip):
        return self.anonymize_ipv4(ip, ':')

    def anonymize_ipv4(self, ip, separator='.'):
        split_ip = ip.split(separator)
        split_ip[-1] = '0'
        return separator.join(split_ip)

    def get_url(self):
        actual_url = self.context.REQUEST['ACTUAL_URL']
        server_url = self.context.REQUEST['SERVER_URL']
        return actual_url.replace('%s' % server_url, '')

    def get_cookie(self):
        js_utma = self.context.REQUEST.get('__utma', '')
        js_utmz = self.context.REQUEST.get('__utmz', '')

        if js_utma and js_utmz:
            cookie = (
                '__utma=%(js_utma)s;+'
                '__utmz=%(js_utmz)s;'
            )
            return cookie % {'js_utma': js_utma, 'js_utmz': js_utmz}
        else:
            cookie = (
                '__utma=%(cookie_nr)s.%(random_nr)s.%(today)s.%(today)s.%(today)s.3;+'
                '__utmz=%(cookie_nr)s.%(today)s.2.2.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none);'
            )
            return cookie % {
                'cookie_nr': randint(10000000, 99999999),
                'random_nr': randint(1000000000, 2147483647),
                'today': int(time()),
            }
