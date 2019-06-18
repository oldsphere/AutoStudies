import os

import logging
logger = logging.getLogger(__name__)

try:
    import xlwings as xw
except ImportError:
    raise ImportError("xwings could not be found")

class ExcelResult:

    def __init__(self, filename):
        self.name = os.path.basename(filename).split('.')[0]
        self._file = filename
        self.wb = None
        self.visible = False
        logger.info('Load case %s' %  self.name)

    def get_cell(self, cell_route, sheet=0):
        ''' Get the value to a cell_route '''

        self.open()
        return self.wb.sheets[sheet].range(cell_route).value

    def open(self):
        if not self.wb:
            xw.App(visible=self.visible)
        self.wb = xw.Book(self._file)
        logger.info('Case "%s" open' % self.name)

    def close(self):
        ''' Close the case '''
        if self.wb:
            app = self.wb.app
            self.wb.close()
            app.quit()
            self.wb = None
            logger.info('Closing workbook "%s"' % self.name)


