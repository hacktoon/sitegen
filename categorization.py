# coding: utf-8

'''
===============================================================================
Mnemonix - The Static Publishing System of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/mnemonix
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

from paging import PageList


class Category:
    '''Define a category of pages'''
    def __init__(self, name):
        self.name = name
        self.pagelist = PageList()

    def add_page(self, page):
        '''To add a book to a category'''
        self.pagelist.insert(page)
    
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

    def add_category(self, category_name):
        '''To create a new category of books'''
        if category_name not in self.items.keys():
            self.items[category_name] = Category(category_name)
        return self.items[category_name]


    def add_page(self, category_name, page):
        '''To add a book to a specific category in a list'''
        if not category_name:
            return
        if category_name not in self.items.keys():
            self.add_category(category_name)
        self.items[category_name].add_page(page)