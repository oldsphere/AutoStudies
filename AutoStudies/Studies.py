from .Auxiliar import ParameterCombiner, FoldNameCreator, NameCreator
from .Path import Path

import logging
logger = logging.getLogger(__name__)

class Study:
    def __init__(self):
        self.namer = NameCreator('case-')
        self._cases = []
        self._isoCases = []
        self._parameters = ParameterCombiner()
        self._basecase = None
        logger.info('created new Study')

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
        logger.info('running study')
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

    def get_cases(self):
        return self._cases

    def clearAll(self):
        for case in self._cases:
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

        cmd, *atr = command.split('.')
        cmd = 'set_'+cmd
        atr = '.'.join(atr)
        return lambda x,y: getattr(x, cmd)(atr, y)


class FoldStudy(Study):
    ''' Study that create the cases in a specified folder '''
    def __init__(self, casefold):
        super().__init__()
        self._casefold = Path(casefold)
        if not self._casefold.exists():
            self._casefold.mkdir()
        self.namer = FoldNameCreator(casefold, 'case-')
        logger.info('created new FoldStudy')

