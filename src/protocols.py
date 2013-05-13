"""
/***************************************************************************
UploadActivity
A QGIS plugin
Upload activity to OLA platform
                             -------------------
begin                : 2012-04-05 Holy Thursday
copyright            : (C) 2012 by Adrian Weber
email                : adrian.weber@cde.unibe.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import QByteArray
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QString
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtNetwork import QNetworkRequest
import simplejson as json

class SettingsProtocol(QObject):

    readSignal = pyqtSignal(bool, int, QString)

    def __init__(self, host, user, password):
        QObject.__init__(self)

        # Set the host
        self.host = host
        # Create a base64 encoded credential string from user name and password.
        # This is required for the HTTP basic access authentication, compare
        # also http://en.wikipedia.org/wiki/Basic_access_authentication
        self.userlogin = "%s:%s" % (user, password)
        self.login = "Basic " + QByteArray(self.userlogin).toBase64()

        # Create a new QNetworkAccessManager and connect it to the
        # authenticationRequired signal
        self.manager = QNetworkAccessManager(self)
        #self.connect(self.manager, SIGNAL("authenticationRequired( QNetworkReply*, QAuthenticator* )"), self.slotAuthenticationRequired)

    def read(self):
        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        url = "%s/config/geometrytaggroups" % self.host

        qUrl = QUrl(url)
        self.request = QNetworkRequest(qUrl)
        self.request.setRawHeader("Authorization", self.login)

        self.request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.manager.get(self.request)

        return url

    def readRequestFinished(self, reply):
        # Get the HTTP status code from the reply
        self.httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        data = reply.readAll()

        # Check the status code see also http://en.wikipedia.org/wiki/HTTP_status_code
        # In case of a successful upload we get a 201 status code back and the
        # "stylePosted" signal is emitted with the first parameter set to True.
        # If the query didn't succeed, the status code is 4xx indicating that
        # the host was not found, the authentication failed or a forbidden
        # action in case a style with the same name already exists. It's up to
        # the receiver to handle these status codes.
        self.readSignal.emit(self.httpStatusCode in (200, 201), self.httpStatusCode, QString(data))


class ActivityProtocol(QObject):

    # SIGNAL that is emitted after activities have been read
    readSignal = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after a new activity has been added
    created = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after an existing activity has been updated
    updated = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after an activity has been deleted
    deleted = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after activities have been counted
    counted = pyqtSignal(bool, int, QString)

    def __init__(self, host, user, password):
        QObject.__init__(self)

        # Set the host
        self.host = host
        # Create a base64 encoded credential string from user name and password.
        # This is required for the HTTP basic access authentication, compare
        # also http://en.wikipedia.org/wiki/Basic_access_authentication
        self.userlogin = "%s:%s" % (user, password)
        self.login = "Basic " + QByteArray(self.userlogin).toBase64()

        # Create a new QNetworkAccessManager and connect it to the
        # authenticationRequired signal
        self.manager = QNetworkAccessManager(self)
        #self.connect(self.manager, SIGNAL("authenticationRequired( QNetworkReply*, QAuthenticator* )"), self.slotAuthenticationRequired)


    def update(self, rawBody):
        """
        Update an activity using a POST request
        """
        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.updateRequestFinished)

        url = "%s/activities" % self.host
        qurl = QUrl(url)
        self.request = QNetworkRequest(qurl)
        self.request.setRawHeader("Authorization", self.login)
        self.request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.manager.post(self.request, QString(json.dumps(rawBody)).toUtf8())

        return url

    def updateRequestFinished(self, reply):
        self.disconnect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.updateRequestFinished)

        # Get the HTTP status code from the reply
        self.httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        #httpReasonPhrase = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute).toString()

        data = reply.readAll()

        self.updated.emit(self.httpStatusCode in (200, 201), self.httpStatusCode, QString(data))

    def read(self, extent):
        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        # Limit the longitude and latitutde maximum boundaries
        xmin = extent.xMinimum() if extent.xMinimum() >= -180 else -180
        ymin = extent.yMinimum() if extent.yMinimum() >= -90 else -90
        xmax = extent.xMaximum() if extent.xMaximum() <= 180 else 180
        ymax = extent.yMaximum() if extent.yMaximum() <= 90 else 90

        url = "%s/activities/json?bbox=%d,%d,%d,%d" % (self.host, xmin, ymin, xmax, ymax)

        qUrl = QUrl(url)
        self.request = QNetworkRequest(qUrl)
        self.request.setRawHeader("Authorization", self.login)

        self.request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.manager.get(self.request)

        return url

    def readRequestFinished(self, reply):
        # Get the HTTP status code from the reply
        self.httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        #data = str("a")
        data = reply.readAll()

        # Check the status code see also http://en.wikipedia.org/wiki/HTTP_status_code
        # In case of a successful upload we get a 201 status code back and the
        # "stylePosted" signal is emitted with the first parameter set to True.
        # If the query didn't succeed, the status code is 4xx indicating that
        # the host was not found, the authentication failed or a forbidden
        # action in case a style with the same name already exists. It's up to
        # the receiver to handle these status codes.
        self.readSignal.emit(self.httpStatusCode in (200, 201), self.httpStatusCode, QString(data))

    def readById(self, id):
        """

        """
        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readByIdRequestFinished)

        # Get the latest version of the activity with this id
        url = "%s/activities/json/%s?geometry=full" % (self.host, id)

        qUrl = QUrl(url)
        self.request = QNetworkRequest(qUrl)
        #self.request.setRawHeader("Authorization", self.login)

        self.manager.get(self.request)

        return url


    def readByIdRequestFinished(self, reply):

        # Get the HTTP status code from the reply
        self.httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        data = reply.readAll()

        self.readSignal.emit(self.httpStatusCode in (200, 201), self.httpStatusCode, QString(data))

class StakeholderProtocol(QObject):

    # SIGNAL that is emitted after stakeholders have been read
    readSignal = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after a new stakeholder has been added
    created = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after an existing activity has been updated
    updated = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after an activity has been deleted
    deleted = pyqtSignal(bool, int, QString)

    # SIGNAL that is emitted after activities have been counted
    counted = pyqtSignal(bool, int, QString)

    def __init__(self, host, user, password):
        QObject.__init__(self)

        # Set the host
        self.host = host
        # Create a base64 encoded credential string from user name and password.
        # This is required for the HTTP basic access authentication, compare
        # also http://en.wikipedia.org/wiki/Basic_access_authentication
        self.userlogin = "%s:%s" % (user, password)
        self.login = "Basic " + QByteArray(self.userlogin).toBase64()

        # Create a new QNetworkAccessManager and connect it to the
        # authenticationRequired signal
        self.manager = QNetworkAccessManager(self)
        
        #self.connect(self.manager, SIGNAL("authenticationRequired( QNetworkReply*, QAuthenticator* )"), self.slotAuthenticationRequired)


    def read(self, ** kwargs):

        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        params = []

        try:
            queryable = kwargs['queryable']
            params.append({'queryable': queryable})
            queryableList = QString(queryable).split(',')
        except KeyError:
            pass

        for key, value in kwargs.items():
            if QString(key).split("__")[0] in queryableList:
                params.append({key: value})

        url = "%s/stakeholders?" % self.host
        for p in params:
            url = "%s%s=%s&" % (url, p.keys()[0], p.values()[0])

        qUrl = QUrl(url)
        # Create a new request
        request = QNetworkRequest(qUrl)
        request.setRawHeader("Authorization", self.login)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.manager.get(request)

        return url

    def readRequestFinished(self, reply):
        # Get the HTTP status code from the reply

        self.disconnect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        # Check the status code see also http://en.wikipedia.org/wiki/HTTP_status_code
        # In case of a successful upload we get a 201 status code back and the
        # "stylePosted" signal is emitted with the first parameter set to True.
        # If the query didn't succeed, the status code is 4xx indicating that
        # the host was not found, the authentication failed or a forbidden
        # action in case a style with the same name already exists. It's up to
        # the receiver to handle these status codes.
        self.readSignal.emit(httpStatusCode in (200, 201), httpStatusCode, QString(reply.readAll()))

    def add(self, stakeholder):

        self.connect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        url = "%s/stakeholders" % self.host

        qurl = QUrl(url)
        # Create a new request
        request = QNetworkRequest(qurl)
        request.setRawHeader("Authorization", self.login)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        wrapperObj = {}
        
        if len(stakeholder) > 0:
            wrapperObj['stakeholders'] = [s.createDiff(None) for s in stakeholder]
        else:
            wrapperObj['stakeholders'] = [stakeholder.createDiff(None)]

        rawBody = json.dumps(wrapperObj, sort_keys=True, indent=4 * ' ')
        self.manager.post(request, rawBody)

        return url, rawBody

    def addRequestFinished(self, reply):

        self.disconnect(self.manager, SIGNAL("finished( QNetworkReply* )"), self.readRequestFinished)

        httpStatusCode = int(reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toString())

        self.created.emit(httpStatusCode in (200, 201), httpStatusCode, QString(reply.readAll()))