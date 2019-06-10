import unittest

import sys
sys.path.insert(0, '..')

import os

from AutoStudies import FolderCase

class dummyFoldCase(FolderCase):
    def run():
        pass
    def post():
        pass


class TestFolderCase(unittest.TestCase):
    def test_Creation(self):
        ''' test FolderCase creation'''
        # Not creation of AbstractClass
        self.assertRaises(TypeError, FolderCase)

        # Not creation if unexisting file
        self.assertRaises(FileNotFoundError, dummyFoldCase, 'unexisting_folder')

        # Normal creation
        os.mkdir('dummy')
        case = dummyFoldCase('dummy')
        os.rmdir('dummy')

    def test_Rename(self):
        ''' Test FolderCase.set_name() '''
        os.mkdir('dummy')
        os.mkdir('dummy2')
        case = dummyFoldCase('dummy')
        case2 = dummyFoldCase('dummy2')

        # Set a non-existant name
        case.set_name('new_dummy', overwrite=False)
        if os.path.exists('dummy') or not os.path.exists('new_dummy'):
            raise Exception('Behavior unexpected')

        # Protect if overwrite flag is down
        self.assertRaises(OSError, case2.set_name,
                          **{'name':'new_dummy', 'overwrite':False})
        if not os.path.exists('dummy2'):
            raise Exception('Behavior unexpected')

        # Overwrite case if possible
        case2.set_name('new_dummy', overwrite=True)
        if os.path.exists('dummy2') or not os.path.exists('new_dummy'):
            raise Exception('Behavior unexpected')

        case2.remove()
        if os.path.exists('new_dummy'):
            raise Exception('Behavior unexpected')

    def test_Clone(self):
        ''' Test FolderCase.clone() method '''
        os.mkdir('dummy3')
        f = open(os.path.join('dummy3', 'file1'), 'w').close()
        f = open(os.path.join('dummy3', 'file2'), 'w').close()
        f = open(os.path.join('dummy3', 'file3'), 'w').close()

        # Add essential files
        case = dummyFoldCase('dummy3')
        case.set_essentialFiles(['file1'])
        case.add_essentialFile('file2')

        # Check clone creation
        ncase = case.clone()
        if not os.path.exists('dummy3-clone'):
            raise Exception('Behavior unexpected')

        # Check copied files
        path = ncase.GetPath()
        file_list = path.ls()
        if not 'file1' in file_list or \
           not 'file2' in file_list or \
           'file3' in file_list:
            raise Exception('Behavior unexpected')

        ncase.remove()
        if os.path.exists('dummy3-clone'):
            raise Exception('Behavior unexpected')
        case.remove()

    def test_Clear(self):
        ''' Test FolderCase.clear() '''

        os.mkdir('dummy4')
        open(os.path.join('dummy4', 'file1'), 'w').close()
        open(os.path.join('dummy4', 'file2'), 'w').close()
        case = dummyFoldCase('dummy4')
        case.add_essentialFile('file1')

        case.clear()
        if not 'file1' in case.GetPath().ls() or \
           'file2' in case.GetPath().ls():
            raise Exception('Behavior unexpected')

        case.remove()

