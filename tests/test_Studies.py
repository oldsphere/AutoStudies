import unittest

import sys
sys.path.insert(0, '..')

import os, re
import shutil
from itertools import product
import numpy as np

from AutoStudies import Study, FoldStudy
from AutoStudies.Cases.AbstractCases import FolderCase
from AutoStudies.Auxiliar import FoldNameCreator
import logging

logging.disable(logging.CRITICAL)


class dummyCase(FolderCase):
    @staticmethod
    def create(folder):
        os.mkdir(folder)
        with open(os.path.join(folder, 'config.txt'), 'w') as config:
            config.writeline = lambda x: config.write(x + '\n')
            config.writeline('param_int = 1')
            config.writeline('param_float = 10.11')
            config.writeline('param_string = "doce"')
            config.writeline('param_negative = -1')
            config.writeline('param_err = False')

        case = dummyCase(folder)
        case.add_essentialFile('config.txt')
        return case

    def set_config(self, param, value):
        self._path.go()
        config = open('config.txt', 'r')
        config_txt = config.read()
        config.close()
        config_txt = re.sub('{}\s*=\s*.+'.format(param),
                            '{} = {}'.format(param, value),
                            config_txt)
        config = open('config.txt', 'w')
        config.write(config_txt)
        config.close()
        self._root.go()

    def get_config(self, param):
        self._path.go()
        config = open('config.txt', 'r')
        config_txt = config.read()
        config.close()
        config_txt = re.findall('{}\s*=\s*(.+)'.format(param), config_txt)
        self._root.go()
        if config_txt:
            return config_txt[-1]

    def run(self):
        if self.get_config('param_err') == 'True':
            raise Exception('Error parameter enabled')
        self._path.go()
        open('DONE', 'w').close()
        self._root.go()

    def post(self):
        self._path.go()
        open('POST', 'w').close()
        self._root.go()

class TestFoldStudy(unittest.TestCase):
    def test_Creation(self):
        study = FoldStudy('newStudy')
        if not os.path.exists('newStudy'):
            raise Exception('Unexpected Behavior')

        # Test Overwrite option
        study = FoldStudy('newStudy')

        os.rmdir('newStudy')

    def test_Generation(self):
        study = FoldStudy('newStudy')
        cas = dummyCase.create('dummyCase')

        study.set_basecase(cas)

        param1 = [2, -4]
        param2 = ['on', 'off']
        param3 = np.linspace(11.1, 16.0, 3)
        study.add_parameter('config.param_int', param1)
        study.add_parameter('config.param_string', param2)
        study.add_parameter('config.param_float', param3)

        cases = list(study.create_cases())
        vals = list(product(param1, param2, param3))
        if len(cases) != len(vals):
            raise Exception('Different lengths!')

        for case, val in zip(cases, vals):
            if case.get_config('param_int') != str(val[0]) or \
               case.get_config('param_string') != str(val[1]) or \
                    case.get_config('param_float') != str(val[2]):
                raise Exception('Not matching creating case')

        shutil.rmtree('newStudy')
        cas.remove()

    def test_EmptyLaunch(self):
        study = FoldStudy('newStudy4')
        study.launch()
        os.rmdir('newStudy4')

    def test_Launch(self):
        study = FoldStudy('newStudy02')
        cas = dummyCase.create('dummyCase02')

        param1 = [2, -4, 5]
        param2 = [True, False]
        study.add_parameter('config.param_int', param1)
        study.add_parameter('config.param_err', param2)

        # Check error if no basecase
        self.assertRaises(AttributeError, study.launch)

        study.set_basecase(cas)
        study.launch()

        for case in study.get_cases():
            if case.get_config('param_err') == 'True' and \
               'DONE' in case.GetPath().ls():
                raise Exception('Running error cases!')
            if case.get_config('param_err') == 'False' and \
               not 'DONE' in case.GetPath().ls():
                raise Exception('Not running normal cases')

        shutil.rmtree('newStudy02')
        cas.remove()

    def test_clearAll(self):
        study = FoldStudy('newStudy03')

        # No error on empty case
        study.clearAll()

        cas = dummyCase.create('dummyCase03')
        study.add_parameter('config.param1', [1,2,3])
        study.set_basecase(cas)
        study.launch()

        fold_list0 = os.listdir('newStudy03')
        if not len(fold_list0) > 0:
            raise Exception('Cases have not been created')

        study.clearAll()
        fold_list1 = os.listdir('newStudy03')
        if fold_list1:
            raise Exception('Cases have not been removed')

        cas.remove()
        os.rmdir('newStudy03')

