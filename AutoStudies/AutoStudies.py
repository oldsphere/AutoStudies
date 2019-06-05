from abc import ABC, abstractmethod
import itertools as iter
import os, re
from .Path import Path
from shutil import copyfile


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
        self._essentialFiles = []
        self._path = Path(folder)
        self._root = self._path.parent.absolute()
        self.name = self._path.name

    def set_name(self, name, overwrite=True):
        self.name = name
        fileExists = (self._root/name).exists()

        if not overwrite and fileExists:
            raise OSError('file already exists')

        if not fileExists:
            self._path.rename(name)
        else:
            [copyfile(str(self._path/f), str(self._root/name/f))
             for f in self._path.ls()]
            self._path.rmtree()
        self._path = Path(self._root/name)

    def clone(self):
        clonepath = self._root/(self.name+'-clone')
        clonepath.mkdir(exist_ok=True)
        [copyfile(str(self._path/f), str(clonepath/f))
         for f in self._path.ls() if str(f) in self._essentialFiles]
        ncase = self.__class__(clonepath)
        return ncase

    def clear(self):
        ''' Remove all the non-essential files '''
        [os.remove(str(self._path/f)) for f in self._path.ls()
         if not str(f) in self._essentialFiles]

    def remove(self):
        ''' Remove the case '''
        self._path.rmtree()


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

    def set_namer(self, namer):
        ''' Set the namer object '''
        self.namer = namer

    def set_basecase(self, case):
        ''' Set the basecase '''
        self._basecase = case

    def launch(self, post=False):
        ''' Launch the cases '''
        for cas in self.create_cases():
            cas.run()
            if post:
                cas.post()

    def add_parameter(self, command, rng):
        ''' Add a new parameter to the study '''
        self._parse_parameter(command, rng)

    def add_cases(self, caseList):
        ''' Add a series of cases '''
        self._isoCases += caseList

    def create_cases(self):
        ''' Create cases '''
        for paramcase in self._parameters.combine():
            ncase = self._basecase.clone()
            [f(ncase, v) for f,v in paramcase]
            ncase.set_name(self.namer.next())
            self._cases.append(ncase)
            yield ncase

        for case in self._isoCases:
            self._cases.append(case)
            yield case

    def clearAll(self):
        for case in self._case:
            case.remove()

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

