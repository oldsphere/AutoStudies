from .AbstractCases import AbstractCase

import os
from functools import partial

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

class OpenFoamCase(AbstractCase):
    def __init__(self, folder):
        self._folder = folder
        self._case = SolutionDirectory(folder)
        self._path = self._case.name
        self.name = os.path.basename(self._path)

        self.__dict__.update(
            {
            'set_snappyHexMesh' : partial(self.set_dictSetting, dictName='snappyHexMesh'),
            'set_fvSchemes' : partial(self.set_dictSetting, dictName='fvSchemes'),
            'set_fvSolution' : partial(self.set_dictSetting, dictName='fvSolution'),
            }
        )

    def set_name(self, name):
        ''' handle the case renaming '''
        pass

    def runApp(self, app, args=kwargs):
        ''' Run an application with the specified arguments '''

        cmd = [app, '-case', self._path]
        cmd += [f'-{k}',{v} for k,v in kwargs.items()]
        return UtilityRunner(cmd).start()

    def clone(self, newName=None):
        ''' Creates a clone of current case '''

        if not newName: newName = self._path + '_clone'
        cloned_case = self._case.cloneCase(newName)
        ncase = self.__class__(cloned_case.name)
        return ncase


    def set_dictSettings(self, dictName, setting, value):
        ''' Change a dictionary value '''
        f = self.findFile(dictName)
        if not f:
            raise OSError(f'no "{dictName}" found in the case {self.name})
        if len(f) > 1:
            raise OSError(f'multiple "{dictName}" found!')

        dictFile = OpenFoamDictionary(f[0])
        dictFile.set_parameter(setting, value)
        dictFile.writeFile()

    def findFile(self, filename):
        return [os.path.join(root, filename)
                for root, dirs, files in os.walk(self._path)
                if filename in files
               ]


class OpenFoamDictionary(ParsedParameterFile):
    ''' Include resursive setting '''

    def __init__(self, filepath):
        super().__init__(filepath)
        self.name = os.path.basename(self.name)

    @staticmethod
    def _set(foamDict, parameter, value):
        ''' recursive setting '''
        if '.' in parameter:
            subdict, *new_parameter = parameter.split('.')
            return OpenFoamDictionary._set(
                foamDict[subdict],
                '.'.join(new_parameter),
                value
            )

        if not parameter in foamDict.keys():
            raise Exception(
                'There is not parameter {} in {}' \
                .format(parameter, foamDict.name)
            )

        foamDict[parameter] = value

    def set_parameter(self, parameter, value):
        return self._set(self.content, parameter, value)

