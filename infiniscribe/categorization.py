# coding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

from .paging import PageList


class Category:
    '''Define a category of pages'''
    def __init__(self, idt):
        self.props = {'id': idt}
        self.pagelist = PageList()

    def add_page(self, page):
        '''To add a book to a category'''
        self.pagelist.insert(page)

    def __setitem__(self, key, value):
        self.props[key] = value

    def __getitem__(self, key):
        return self.props.get(key)

    def get_dict(self):
        return self.props
    
    def paginate(self):
        '''To sort books in the shelves'''
        self.pagelist.paginate()


class CategoryList:
    '''Define a list of categories'''
    def __init__(self):
        self.items = {}

    def __iter__(self):
        for category in self.items.values():
            yield category

    def __getitem__(self, key):
        return self.items.get(key)

    def add_category(self, category_key):
        '''To create a new category of books'''
        if category_key not in self.items.keys():
            self.items[category_key] = Category(category_key)
        return self.items[category_key]

    def add_page(self, category_title, page):
        '''To add a book to a specific category in a list'''
        if category_title not in self.items.keys():
            self.add_category(category_title)
        self.items[category_title].add_page(page)
