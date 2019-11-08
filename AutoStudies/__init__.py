from AutoStudies.Auxiliar import *
from AutoStudies.Studies import *
from AutoStudies.Path import *

# Import cases
from AutoStudies.Cases.SolsticeCase import SolsticeCase

try:
    from AutoStudies.Cases.ExcelCase import ExcelCase
except ImportError:
    pass

try:
    from AutoStudies.Cases.OpenFoamCase import OpenFoamCase
except ImportError:
    pass


