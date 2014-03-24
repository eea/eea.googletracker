Introduction
============

Server side file download tracking in Google Analytics


A BrowserView is created that makes a request to the Google
Analytics __utm.gif image, just as the JavaScript does.

If __utma and __utmz are present on the REQUEST the value from
these parameters are used, therefore preserving cookie id and
referral paths.

If __utma and __utmz parameters are not present on the REQUEST
these parameters are automatically built and the __utm.gif request
is done as a "direct" hit from a new user.

HTTP/HTTPS GA requests are handled as expected.

In order to properly track the visiting user location the "utmip" parameter
is used. This requires to change the the request to use MO (mobile) in the
GA account id (instead of UA). For example UA-00000-0 will become MO-00000-0.
No change is required in either GA or the portal.


IMPORTANT
---------

If using a caching proxy (e.g. Varnish) you must:

    1. disable caching for urls containing "at_download"
    2. set plone.app.caching to "No cache" for "Content files and images"
       in "Site setup"



Included customisations:

    * at_download.py
    * monkeypatches


at_download.py
--------------

The at_download script has been customised to also call the tracking view.


monkeypatches
-------------

collective.monkeypatcher is used to patch the index_html functions for
ATCTFileContent, ATFile and ATBlob to also call the tracking view.
