from .AutoStudies import FolderCase, Study, CaseLocator
from .decorators import checkcase, timeprint, timefile, casetimer
import os
from yamlParser import createYAMLTree

import numpy as np


class SolsticeCase(FolderCase):
    ''' Basic case for Solstice '''

    def __init__(self, path):
        super().__init__(path)
        self._essentialFiles = ['geometry.yaml', 'receiver.yaml']
        self._solar_dir = '0,90'
        self._nrays = int(1e6)

        self._path.go()
        self.t = createYAMLTree('geometry.yaml')
        self._root.go()

    def run(self):
        ''' Run the case '''
        self._path.go()
        os.system('solstice -D {} -n {} -R {} -f {} > out.log' \
                  .format(self._solar_dir, self._nrays,
                          'receiver.yaml', 'geometry.yaml'))
        self._root.go()

    def rays(self):
        ''' Run the case '''
        self._path.go()
        os.system('solstice -D {} -n 1000 -R {} -p default {} | sed \'1d\' > rays.vtk' \
                  .format(self._solar_dir, 'receiver.yaml', 'geometry.yaml'))
        self._root.go()

    def post(self, *args, **kwargs):
        ''' Post processing the case '''
        self._path.go()
        os.system('solmaps out.log')
        self._root.go()

    def set_geometry(self, param, value):
        ''' Set geometry dictionary values
            format:
                entityName->parameter

            eg:
                primary_reflector->path
        '''

        self._path.go()
        value = self._toStandard(value)
        if '->' in param:
            objName, objParam = param.split('->')
            self.t.entity(name=objName).deepset(**{objParam:value})
        else:
            self.t.deepset(**{param:value})
        self.saveYAML(self.t, 'geometry.yaml')
        self._root.go()

    def set_receiver(self, param, value):
        ''' Set receiver dictionary values '''
        t = createYAMLTree('receiver.yaml')
        objName, objParam = param.split('->')
        t.entity(name=objName).deepset(objParam, value)
        self.saveYAML(t, 'receiver.yaml')

    def set_simulation(self, param, value):
        ''' Set simulation options '''
        if param == 'nrays':
            self._nrays = int(value)
        if param == 'solar_dir':
            self._solar_dir = value
        if param == 'dni':
            self.set_geometry('dni', value)
        if param == 'PC':
            self._path.go()
            self.t.entity(name='receiver') \
                .transform.translation[2] = value
            self.saveYAML(self.t, 'geometry.yaml')
            self._root.go()

    def clone(self):
        ''' Clone the case '''
        ncase = super().clone()
        ncase._solar_dir = self._solar_dir
        ncase._nrays = self._nrays
        return ncase

    @staticmethod
    def _toStandard(value):
        if type(value).__module__ == np.__name__:
            return value.tolist()
        return value

    @staticmethod
    def saveYAML(yamlTree, filename):
        f = open(filename, 'w+')
        f.write(yamlTree.dump())
        f.close()

