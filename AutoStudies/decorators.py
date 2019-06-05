from functools import wraps
import os
import time
from datetime import datetime

#########################
#   Class Decorator     #
#########################

def checkcase(case):
    ''' Add a DONE checking to a FolderCase Object '''
    old_run = case.run

    @wraps(case.run)
    def generateDONE(self=case):
        if not 'DONE' in self._path.ls():
            old_run(self)

            self._path.go()
            os.system('touch DONE')
            self._root.go()
        else:
            print(self.name, 'already done!')
    case.run = generateDONE
    return case

def casetimer(case, logname='timer.log'):
    ''' Add a DONE checking to a FolderCase Object '''
    case.run = timeprint(timefile(case.run, logname))
    case.post = timeprint(timefile(case.post, logname))

    return case



#########################
#   Method Decorator    #
#########################

def string_arguments(*args, **kwargs):
    ''' Parse the argument provided by dot-separated string'''
    arguments = ','.join([str(f) for f in args]) + ',' + \
                ','.join([str(k)+'='+str(v) for k,v in kwargs.items()])
    if arguments[0] == ',':
        arguments = arguments[1:]
    if not arguments:
        return ''
    if arguments[-1] == ',':
        arguments = arguments[:-1]
    return arguments

def timeprint(method):
    ''' Print elapsed time on the method '''
    def timer(*args, **kwargs):
        start = time.time()
        method(*args, **kwargs)
        end = time.time()

        etime_string = args[0].name+'.'
        methodname = '.'.join(method.__qualname__.split('.')[1:])
        arguments = string_arguments(*args[1:], **kwargs)

        print('{}{}({}) - Elapsed time {} s'.format(
            etime_string, methodname, arguments, end-start))

    timer.__qualname__ = method.__qualname__
    return timer

def timefile(method, logname='timer.log'):
    ''' Print elapsed time to file '''
    def timer(*args, **kwargs):
        start = time.time()
        method(*args, **kwargs)
        end = time.time()

        now = datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S')
        etime_string = args[0].name+'.'
        methodname = '.'.join(method.__qualname__.split('.')[1:])
        arguments = string_arguments(*args[1:], **kwargs)

        f = open(logname, 'a')
        print('{}  {}{}({}) - Elapsed time {} s' \
              .format(now,etime_string, methodname, arguments, end-start),
              file=f)
        f.close()


    timer.__qualname__ = method.__qualname__
    return timer

def sendMsg(method, messenger):
    def func(*args, **kwargs):
        start = time.time()
        try:
            method(*args, **kwargs)
            status = 'success'
        except:
            status = 'error'
        end = time.time()
        methodname = '.'.join(method.__qualname__.split('.')[1:])
        messenger.set_name(methodname)
        messenger.set_etime(end-start)
        messenger.set_status(status)
        messenger.send()

    return func
