# -*- coding: utf-8 -*-

class Backend(object):

    def __init__(self):
        pass

    def __not_implemented(self,name):
        raise NotImplementedError(
            "%s is not implemented in subclass '%s'" %(name,self.__class__))

    def get_item(self,id):
        """Get an item with a specific ID

        XXX: id must be some kind of universal identifier. how?
        """
        self.__not_implemented('get_item')

    def get_all_items(self):
        """Get all available items"""
        self.__not_implemented('get_all_items')

    def get_all_item_ids(self):
        """Get all item ids"""
        self.__not_implemented('get_all_item_ids')

    def update_item(self,id,item):
        """Update item properties"""
        self.__not_implemented('update_item')

    def delete_item(self,id):
        """Delete an item with a specific ID"""
        self.__not_implemented('delete_item')

    def delete_all_items(self):
        """Delete all items in the calendar"""
        self.__not_implemented('delete_all_items')

    def create_item(self,item):
        """Create an item with properties from item"""
        self.__not_implemented('create_item')

