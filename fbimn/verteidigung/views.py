from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.memoize.instance import memoize
from Acquisition import aq_acquire, aq_inner
from zope import schema
from zope.formlib import form
from zope.interface import implements, Interface
from DateTime import DateTime
import re

# Product imports
from fbimn.verteidigung import config
from fbimn.verteidigung.interfaces import IVerteidigungView
from fbimn.verteidigung import exampleMessageFactory as _

class VerteidigungEventsView(BrowserView):
    implements(IVerteidigungView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def user_is_anon(self):
        return api.user.is_anonymous()

    @memoize
    def getData(self):
        verteidigung_brains = self.context.portal_catalog.queryCatalog({"portal_type"  : "Verteidigung",
                                                                        "sort_on"      : "start",
                                                                        "sort_order"   : "descending",
                                                                        "sort_limit"   : 10,
                                                                        "review_state" : "published"})
        termine = []
        for brain in verteidigung_brains:
            obj = brain.getObject()
            if obj.hasEventRestriction() and self.user_is_anon(): continue
            termin = dict()
            termin['topic'] = obj.getTopic()

            date = obj.getDate()
            if date:
                termin['startDate'] = str(date.strftime("%d.%m.%y -  %H:%M")) + u' Uhr'
            else:
                termin['startDate'] = u'Unbekannt'

            degree = obj.getEventType()
            if degree:
                degree = re.sub('[^A-Za-z0-9]+', '', degree)
            else:
                degree = ""

            termin['title'] = degree + u' ' + obj.getGraduateName()
            if obj.hasEventRestriction():
                termin['title'] += u' (Sperrvermerk)'
            termin['location'] = obj.getRoom()
            termin['event_url'] = brain.getURL()
            termine += [ termin ]

        self.termine_anzahl = len(termine)
        return termine
