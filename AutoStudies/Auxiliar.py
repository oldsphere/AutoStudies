import os, re
import itertools as iter

import logging
logger = logging.getLogger(__name__)

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
