from abc import ABC, abstractmethod
import os, re
from ..Path import Path
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

    def findFiles(self, regex):
        sep = os.path.sep
        repath = lambda x: sep.join(x.split(sep)[1:])

        return [repath(os.path.join(root, filename))
                 for root, dirs, files in os.walk(str(self._path))
                 for filename in files
                 if re.search(regex, filename)
                ]

    @staticmethod
    def LocateInFileList(fileList, regex):
        matches  = [f
                   for f in fileList
                   if re.search(regex, f)]
        if matches:
            return main_file[0]

