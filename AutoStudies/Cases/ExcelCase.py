from .AbstractCases import AbstractCase
import os, re

import logging
logger = logging.getLogger(__name__)

try:
    import xlwings as xw
except ImportError:
    raise ImportError("xwings could not be found")

class ExcelCase(AbstractCase):
    '''
        Launch an excel case
    '''

    def __init__(self, filename):
        self.name = os.path.basename(filename).split('.')[0]
        self._file = filename
        self.wb = None
        self.visible = False
        logger.info('Created case %s' %  self.name)

    def set_cell(self, cell_route, value, sheet=0):
        ''' Set the value to a cell_route
            The cell route must be of tupe sheetname.C4
        '''

        self.open()
        self.wb.sheets[sheet].range(cell_route).value = value
        logger.debug('Setting {}->{}={}'.format(self.name, cell_route, value))

    def set_name(self, newName):
        ''' Rename the case '''
        self.open()
        new_path = self._RenamePreserveExtension(self._file, newName)
        self.wb.save(new_path)
        self.close()
        os.remove(self._file)
        self._file = new_path
        self.name = os.path.basename(new_path).split('.')[0]

    def run_macro(self, macro_name, macro_args=()):
        ''' Run a Macro '''
        self.open()
        mac = self.wb.macro(macro_name)
        logger.info('Running macro "%s" from workbook "%s"' % (macro_name, self.name))
        mac(*macro_args)

    def open(self):
        if not self.wb:
            xw.App(visible=self.visible)
            logger.info('Case "%s" open' % self.name)
            self.wb = xw.Book(self._file)

    def close(self):
        ''' Close the case '''
        if self.wb:
            app = self.wb.app
            self.wb.close()
            app.quit()
            self.wb = None
            logger.info('Closing workbook "%s"' % self.name)

    def remove(self):
        ''' Remove the case '''
        self.close()
        os.remove(self._file)

    def clone(self):
        ''' Create a copy of itself '''
        self.open()
        new_file = self._RenamePreserveExtension(self._file,
                                                 self.name+'-clone')
        self.wb.save(new_file)
        self.close()
        ncase = self.__class__(new_file)
        ncase.visible = self.visible
        return ncase

    @staticmethod
    def isValidName(name):
        ''' Evaluate if a name is a valid filename '''
        return (name.lower().endwith('.xlsm') or name.lower().endwith('xls')) \
               and not name.startwith('~$')

    @staticmethod
    def _RenamePreserveExtension(old, new):
        ''' Return the new name preserving extension '''
        path = os.path.dirname(old)
        extension = os.path.basename(old).split('.')[-1]
        return os.path.join(path, new + '.' + extension)

