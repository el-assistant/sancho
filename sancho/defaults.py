"""
This module has default import to be used in this project.

Most of the imports here are related to functional programming paradigm in python.

Coding guidelines:
- Functions first
- Use immutables objects
- Separate data from functions, but still define data structure
- Prefer native python libraries and types

In practical terms, we use NamedTuple instead of dict and tuple instead of list.
Additionally, we use NamedTuple from typing instead of namedtuple from
collections because it allows to define data types through hints, which becomes
very handy for code completion. It also provides the possibility to add
docstrings to the data. Data that leaves a module should always be a NamedTuple,
ideally containing only native data types. Providing a docstring for these named
tuples is very important since the data will carry its methods as in OO
programming.

"""

from functools import reduce
from functools import partial
from functools import singledispatch
import functools as ft

import operator as op

from itertools import *
import itertools as itt

from more_itertools import *
import more_itertools as mit


from typing import NamedTuple
from typing import Tuple, Callable
import typing as tp
