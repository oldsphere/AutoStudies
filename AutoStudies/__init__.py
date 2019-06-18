from .Auxiliar import *
from .Studies import *
from .Path import *

# Import cases
from .Cases.SolsticeCase import SolsticeCase
try:
    from .Cases.ExcelCase import ExcelCase
except ImportError:
    pass



