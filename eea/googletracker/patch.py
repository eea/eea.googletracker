from Products.ATContentTypes.content.file import ATCTFileContent
from plone.app.blob.content import IATBlobImage, ATFile


def track_download(context, field):
    try:
        context.restrictedTraverse('@@track_download')(context, field)
    except:
        pass


def ATCTFileContent_index_html(self, REQUEST=None, RESPONSE=None):
    """Make it directly viewable when entering the objects URL
    """
    if REQUEST is None:
        REQUEST = self.REQUEST
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE
    field = self.getPrimaryField()

    ############## PATCH #######
    track_download(self, field)#
    ############################

    data  = field.getAccessor(self)(REQUEST=REQUEST, RESPONSE=RESPONSE)
    if data:
        return data.index_html(REQUEST, RESPONSE)
    # XXX what should be returned if no data is present?



def ATFile_index_html(self, REQUEST=None, RESPONSE=None):
    """Download the file
    """
    field = self.getPrimaryField()

    ############## PATCH #######
    track_download(self, field)#
    ############################

    if field.getContentType(self) in self.inlineMimetypes:
        # return the PDF and Office file formats inline
        return ATCTFileContent.index_html(self, REQUEST, RESPONSE)
    # otherwise return the content as an attachment
    # Please note that text/* cannot be returned inline as
    # this is a security risk (IE renders anything as HTML).
    return field.download(self)

def ATBlob_index_html(self, REQUEST, RESPONSE):
    """ download the file inline or as an attachment """
    field = self.getPrimaryField()

    ############## PATCH #######
    track_download(self, field)#
    ############################

    if IATBlobImage.providedBy(self):
        return field.index_html(self, REQUEST, RESPONSE)
    elif field.getContentType(self) in ATFile.inlineMimetypes:
        return field.index_html(self, REQUEST, RESPONSE)
    else:
        return field.download(self, REQUEST, RESPONSE)
