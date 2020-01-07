from abc import ABC, abstractmethod
from typing import Any
from ..interpreter import InterpreterError
from ..enumerator import Enumerator
from ..decider import Decider
from ..dsl import Node
from ..logger import get_logger
import time



logger = get_logger('tyrell.synthesizer')
INF = 1000

class Synthesizer(ABC):

    _enumerator: Enumerator
    _decider: Decider
    _num_attempts = 0
    _num_solutions = 0

    def __init__(self, enumerator: Enumerator, decider: Decider):
        self._enumerator = enumerator
        self._decider = decider
        self._enumerator.set_decider(decider)
        self.table = None

    def set_table(self, table):
        self.table = table

    @property
    def enumerator(self):
        return self._enumerator

    @property
    def decider(self):
        return self._decider

    def synthesize(self):
        solution = (INF, "")
        '''
        A convenient method to enumerate ASTs until the result passes the analysis.
        Returns the synthesized program, or `None` if the synthesis failed.
        '''
        Synthesizer._num_attempts = 0
        prog = self._enumerator.next()
        while prog is not None:
            Synthesizer._num_attempts += 1
            logger.debug('Enumerator generated: {}'.format(prog))
            logger.info("Attempts " + str(Synthesizer._num_attempts))
            try:
                res = self._decider.analyze(prog)
                if res.is_ok():
                    logger.debug(
                        'Program accepted after {} attempts'.format(Synthesizer._num_attempts))
                    logger.info("Attempts " + str(Synthesizer._num_attempts))
                    logger.info("Found program " + str(prog) + " with score " + str(self.table.last_norm))
                    Synthesizer._num_solutions += 1
                    if solution[0] > self.table.last_norm:
                        solution = (self.table.last_norm, str(prog))
                    prog = self._enumerator.next()
                    #return prog
                else:
                    info = res.why()
                    logger.debug('Program rejected. Reason: {}'.format(info))
                    self._enumerator.update(info)
                    prog = self._enumerator.next()
            except InterpreterError as e:
                pass
        logger.info("Number of attempts {}".format(Synthesizer._num_attempts))
        logger.info("Number of solutions {}".format(Synthesizer._num_solutions))
        logger.debug(
            'Enumerator is exhausted after {} attempts'.format(Synthesizer._num_attempts))
        return solution[1]
