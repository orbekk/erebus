# -*- coding: utf-8 -*-
"""

CalDAV interface class that extends DAV.dav_interface.

Subclasses must implement the query_calendar method

TODO: add extra properties from the RFC here
"""

from DAV.iface import *

class caldav_interface(dav_interface):
    TAKE_DOC = True

    PROPS = dav_interface.PROPS.copy()
    PROPS['urn:ietf:params:xml:ns:caldav'] = ('calendar-home-set',
                                              'calendar-user-address-set')

    M_NS = dav_interface.M_NS.copy()
    M_NS['urn:ietf:params:xml:ns:caldav'] = '_get_caldav'

    def get_prop(self,uri,ns,propname,doc):
        """ return the value of a given property

        We need to redefine this to handle properties with '-' in them

        uri        -- uri of the object to get the property of
        ns        -- namespace of the property
        pname        -- name of the property
        """
        self._doc = doc

        if self.M_NS.has_key(ns):
            prefix=self.M_NS[ns]
        else:
            raise DAV_NotFound
        mname= prefix + "_" + propname.replace('-','_')

        try:
            m=getattr(self,mname)
            r=m(uri)
            return r
        except AttributeError:
            raise DAV_NotFound

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
    
