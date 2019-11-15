from .AbstractCases import FolderCase

import os, re
import subprocess as sub

import logging
logger = logging.getLogger(__name__)

class APDLCase(FolderCase):

    def __init__(self, filename):
        super().__init__(filename)

        self.macro_files = self.findFiles('.inp')

        self.main_file = self.LocateInFileList(self.macro_files, 'main.inp')
        self.parameter_file = self.LocateInFileList(self.macro_files, 'parameters?.inp')

        self.outlog = 'out.log'
        self._app = 'apdl'


    def run(self):
        if not self.main_file:
            raise Exception('No main.inp has been found in case {}'
                            .format(self.name))
        self._path.go()
        sub.run(
            [self._app, '-i', self.main_file,
             '-j', self.name, '-b', '-o', self.outlog],
        )
        self._root.go()


    def set_parameter(self, parameter, value):
        if not self.parameter_file:
            raise Exception('No parameter.inp has been found in case {}'
                            .format(self.name))

        with open(self.parameter_file, 'r') as f:
            content = f.read()
        raise Exception('Not implemented method')
