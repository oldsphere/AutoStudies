from .AbstractCases import AbstractCase
import os, re

import logging
logger = logging.getLogger(__name__)

try:
    import xlwings
except ImportError
    raise ImportError("xwings could not be found")

class ExcelCase(AbstractCase):
    '''
        Launch an excel case
    '''

    def __init__(self, filename):
        self.name = os.path.basename(filename).split('.')[-1]
        self._file = filename
        self.wb = None
        self.visible = False
        logger.info('Created case %s' %  self.name)

    def set_cell(self, cell_route, value):
        ''' Set the value to a cell_route
            The cell route must be of tupe sheetname.C4
        '''

        self.open()
        sheet, cell = split(cell_route, '.')

        cell = self.wb.sheets[sheet].cell = value
        logger.debug('Setting {}->{}={}'.format(self.name, cell_route, value))

    def set_name(self, newName):
        ''' Rename the case '''
        self.open()
        path = os.path.dirname(self._file)
        extension = os.path.basename(self._file)
        # Check the extension of the newfile
        self.wb.save(newName)
        self.close()
        os.remove(self._file)

    def open(self):
        if not self.wb:
            xw.App(visible=self.visible)
        self.wb = xw.Book(self._file)
        logger.info('Case "%s" open' % self.name)

    def close(self):
        ''' Close the case '''
        if self.wb:
            app = wb.app
            self.wb.close()
            app.quit()
            self.wb = None
            logger.info('Closing workbook ', self.name)

    def remove(self):
        ''' Remove the case '''
        os.remove(self._file)

    def clone(self):
        ''' Create a copy of itself '''
        self.open()
        new_file = self._file + '-clone')
        self.wb.save(new_file)
        ncase = self.__class__(new_file)
        ncase.visible = self.visible
        return ncase


class ExcelMacroCase(ExcelCase):

    def run(self):
        ''' Run the case '''
        self.open()
        mac = wb.macro('Calcula')
        logger.info('Running %s macro from workbook %s' % ('Calcula', self.name))
        mac()
        self.wb.save()
        self.close()

