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
            'set_snappyHexMesh' : partial(self.set_dictSettings, 'snappyHexMeshDict'),
            'set_fvSchemes' : partial(self.set_dictSettings, 'fvSchemes'),
            'set_fvSolution' : partial(self.set_dictSettings, 'fvSolution'),
            }
        )

    def set_name(self, name):
        ''' handle the case renaming '''
        new_path = os.path.join( os.path.dirname(self._path), name )
        os.rename(self._path, new_path)
        self._case = SolutionDirectory(new_path)
        self._path = new_path
        self.name = name

    def run(self):
        pass

    def runApp(self, app, args={}, quiet=False):
        ''' Run an application with the specified arguments '''

        quiet_options = {
            'silent' : True if quiet else False,
        }

        cmd = [app, '-case', self._path]
        cmd += sum([['-{}'.format(k),v] for k,v in args.items()], [])
        return UtilityRunner(cmd, **quiet_options).start()

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
            raise OSError('no "{}" found in the case {}'
                          .format(dictName, self.name))
        if len(f) > 1:
            raise OSError('multiple "{}" found!'.format(dictName))

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
        self.basename = os.path.basename(self.name)

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
            return -1

        foamDict[parameter] = value

    def set_parameter(self, parameter, value):

        out = self._set(self.content, parameter, value)
        if out == -1:
            raise Exception(
                'There is not parameter {} in {}' \
                .format(parameter, self.basename)
            )
        return out

