# -*- coding: utf-8 -*-
"""

CalDAV interface class that extends DAV.dav_interface.

Subclasses must implement the query_calendar method

TODO: add extra properties from the RFC here
"""

from DAV.iface import *

class caldav_interface(dav_interface):

    def query_calendar(self,uri,filter,calendar_data,what):
        """This is the filter from a calendar-query

        This method should return the calendar_data in `uri' after
        applying the filter. Only elements in calendar_data should be
        returned

        uri: the calendar uri
        filter: the CALDAV:filter element from the query
        calendar_data: the CALDAV:calendar-data from the query
        """
        raise NotImplementedError(
            'Please implement query_calendar in your subclass')
    
