from .AbstractCases import FolderCase

from collections import OrderedDict
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


        self.parameterInfo = []
        self.parameters = []

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


\t    def update_parameters(self):
        ''' Parse the available parameter '''
        if not self.parameter_file:
            raise Exception('No parameter.inp has been found in case {}'
                            .format(self.name))

        content = (open(self.LocalPath(self.parameter_file), 'r')
                   .read()
                   .split('\n'))

        paramList = []

        for line in content:
            parameter = re.search('^\s*(.+)\s*=', line)
            if not parameter:
                continue
            parameter = parameter.group(1)

            value = re.search('=\s*([^ ]+)', line)
            value = value.group(1)

            comment = re.search('!(.+)$', line)
            if comment:
                comment = comment.group(1)

            paramList.append(OrderedDict({
                'parameter' : parameter,
                'value'     : value,
                'comment'   : comment
            }))

        self.parameterInfo = paramList
        self.parameters = [p['parameter'] for p in paramList]


    def set_parameter(self, parameter, value):
        if not self.parameter_file:
            raise Exception('No parameter.inp has been found in case {}'
                            .format(self.name))

        paramInfo = [p for p in self.parameterInfo
                     if p['parameter'] == parameter][0]
        comment = '\t!'+ paramInfo['comment'] if paramInfo['comment']  \
                  else  ''

        paramFilePath = self.LocalPath(self.parameter_file)
        with open(paramFilePath, 'r') as f:
            content = f.read()
            newContent = re.sub('(?<={})\s*=([^\n]+)'.format(parameter),
                                '={}'.format(value) + comment,
                                content)

        print(newContent)
        #with open(paramFilePath, 'w') as f:
        #    f.write(newContent)




