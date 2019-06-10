from abc import ABC, abstractmethod
import itertools as iter
import os, re
from .Path import Path
from shutil import copyfile

import logging
logger = logging.getLogger(__name__)

class AbstractCase(ABC):
    def __init__(self):
        self.name = 'defcase'

    def set_name(self, name):
        self.name = name

    @abstractmethod
    def run(self):
        ''' Run the case '''
        pass

    @abstractmethod
    def clone(self):
        ''' Create a copy of itself '''
        pass

    def post(self, **kwargs):
        pass


class FolderCase(AbstractCase):
    ''' Case definition content in a folder '''

    def __init__(self, folder):
        if not os.path.exists(folder):
            raise FileNotFoundError()
        self._essentialFiles = []
        self._path = Path(folder)
        self._root = self._path.parent.absolute()
        self.name = self._path.name

    def set_name(self, name, overwrite=True):
        ''' Rename the case '''
        self.name = name

        fileExists = (self._root/name).exists()

        if not overwrite and fileExists:
            logger.error('file already exists and no overwrite is set')
            raise OSError('file already exists')

        if not fileExists:
            self._path.rename(name)
            logger.info('Renaming case %s' % self.name)
        else:
            [copyfile(str(self._path/f), str(self._root/name/f))
             for f in self._path.ls()]
            self._path.rmtree()
            logger.info('Overwriting case %s' % self.name)
        self._path = Path(self._root/name)

    def set_essentialFiles(self, file_list):
        ''' Reset the essential file list '''
        self._essentialFiles = file_list

    def add_essentialFile(self, filename):
        ''' Include a new file to the essential list '''
        self._essentialFiles.append(filename)

    def GetPath(self):
        ''' Return the Path Object '''
        return self._path

    def clone(self):
        ''' Create a copy of the case for the relevant files '''

        clonepath = self._root/(self.name+'-clone')
        clonepath.mkdir(exist_ok=True)
        logger.debug('created folder ' + self.name + '-clone')
        [copyfile(str(self._path/f), str(clonepath/f))
         for f in self._path.ls() if str(f) in self._essentialFiles]
        logger.debug('copied relevant files to cloned folder')
        ncase = self.__class__(str(clonepath))

        logger.info('creating clone of ' + self.name)

        return ncase

    def clear(self):
        ''' Remove all the non-essential files '''
        [os.remove(str(self._path/f)) for f in self._path.ls()
         if not str(f) in self._essentialFiles]
        logger.info('case %s cleaned' % self.name)

    def remove(self):
        ''' Remove the case '''
        self._path.rmtree()
        logger.info('case %s removed' % self.name)


class CaseLocator(list):
    def __init__(self, caseType):
        self._casetype = caseType
        super().__init__()

    def locate_byNamer(self, namer, folder='.'):
        ''' Use a namer to locate the cases on a folder'''
        self.clear()
        for f in os.listdir(folder):
            if namer.validate(f):
                try:
                    casFold = os.path.abspath(os.path.join(folder, f))
                    cas = self._casetype(casFold)
                    self.append(cas)
                except:
                    print('Error with "%s"' % f)

    def filterByName(self, name, hard=False):
        new = CaseLocator(self._casetype)
        if hard==True:
            new += [c for c in self if name == c.name]
            return new
        new += [c for c in self if name in c.name]
        return new

    @staticmethod
    def nest_getattr(obj, param):
        params = param.split('.')
        cobj = obj
        if len(params) > 2:
            for p in params[:-1]:
                cobj = getattr(cobj, p)
        return getattr(cobj, params[-1])


class Study:
    def __init__(self):
        self.namer = NameCreator('case-')
        self._cases = []
        self._isoCases = []
        self._parameters = ParameterCombiner()
        self._basecase = None
        logger.info('created new study')

    def set_namer(self, namer):
        ''' Set the namer object '''
        self.namer = namer
        logger.info('Switched study namer')

    def set_basecase(self, case):
        ''' Set the basecase '''
        self._basecase = case
        logger.info('Set %s as the basecase of the study' % case.name)

    def launch(self, post=False):
        ''' Launch the cases '''
        self.info('running study')
        for cas in self.create_cases():
            try:
                cas.run()
                if post:
                    cas.post()
            except:
                logging.error('case %s has failed during run' % cas.name)
                continue

    def add_parameter(self, command, rng):
        ''' Add a new parameter to the study '''
        self._parse_parameter(command, rng)
        logger.info('Study has added a new parameter')

    def add_cases(self, caseList):
        ''' Add a series of cases '''
        self._isoCases += caseList
        logger.info('Study has added %s isolated cases' % len(caseList))

    def create_cases(self):
        ''' Create cases '''
        for paramcase in self._parameters.combine():
            ncase = self._basecase.clone()
            [f(ncase, v) for f,v in paramcase]
            ncase.set_name(self.namer.next())
            self._cases.append(ncase)
            logger.debug('Study has created case %s' % ncase.name)
            yield ncase

        for case in self._isoCases:
            self._cases.append(case)
            yield case

    def clearAll(self):
        for case in self._case:
            case.remove()
        logger.info('Study has been cleaned')


    # - Private Methods -

    def _parse_parameter(self, command, rng):
        ''' Parse the options and the range '''

        self._parameters.add(self._parse_command(command), rng)

    @staticmethod
    def _parse_command(command):
        '''Parse case setters command as command = "config.argument"
           Return case.set_config(argument, x) anonymous function
        '''

        cmd, atr = command.split('.')
        cmd = 'set_'+cmd
        return lambda x,y: getattr(x, cmd)(atr, y)


class FoldStudy(Study):
    ''' Study that create the cases in a specified folder '''
    def __init__(self, casefold):
        super().__init__()
        self._casefold = Path(casefold)
        if not self._casefold.exists():
            self._casefold.mkdir()
        self.namer = FoldNameCreator(casefold, 'case-')


class StudyNoRecord(Study):
    ''' Extract sensible information without recording all the output data '''
    pass


class Optimizer(Study):
    ''' Optimize a case based on few parameters'''
    pass


class ParameterCombiner:
    def __init__(self):
        self._f = []
        self._ranges = []

    def add(self, f, rng):
        self._f.append(f)
        self._ranges.append(rng)

    def combine(self):
        if not self._f:
            return
        for v in iter.product(*self._ranges):
            v = (self.denumpyfy(vv) for vv in v)
            yield list(zip(self._f, v))

    @staticmethod
    def denumpyfy(arg):
        if hasattr(arg, 'tolist'):
            return arg.tolist()
        return arg


class NameCreator:
    ''' Create a name-pattern '''
    def __init__(self, basename=None, start=0):
        self.basename = basename
        self.ind = start

    def set_basename(self, basename):
        self.basename = basename

    def next(self):
        ''' return next name '''
        newName = self.basename+str(self.ind)
        self.ind += 1
        return newName

    def validate(self, name):
        if re.match('{}\d+'.format(self.basename), name):
            return True
        return False


class FoldNameCreator(NameCreator):
    def __init__(self, folder,  basename=None, start=0):
        super().__init__()
        self._folder = folder
        self.basename = os.path.join(self._folder, basename)

    def set_basename(self, basename):
        self.basename = os.path.join(self._folder, basename)

    def set_folder(self, folder):
        self._folder = folder

