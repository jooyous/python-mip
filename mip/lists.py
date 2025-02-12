from collections.abc import Sequence
from typing import List
from mip.constants import BINARY, CONTINUOUS, INF
from mip.entities import Column, Constr, LinExpr, Var


class VarList(Sequence):
    """ List of model variables (:class:`~mip.model.Var`).

        The number of variables of a model :code:`m` can be queried as
        :code:`len(m.vars)` or as :code:`m.num_cols`.

        Specific variables can be retrieved by their indices or names.
        For example, to print the lower bounds of the first
        variable or of a varible named :code:`z`, you can use, respectively:

        .. code-block:: python

            print(m.vars[0].lb)

        .. code-block:: python

            print(m.vars['z'].lb)
    """

    def __init__(self, model: "Model"):
        self.__model = model
        self.__vars = []

    def add(self,
            name: str = "",
            lb: float = 0.0,
            ub: float = INF,
            obj: float = 0.0,
            var_type: str = CONTINUOUS,
            column: Column = None) -> Var:
        if not name:
            name = 'var({})'.format(len(self.__vars))
        if var_type == BINARY:
            lb = 0.0
            ub = 1.0
        new_var = Var(self.__model, len(self.__vars))
        self.__model.solver.add_var(obj, lb, ub, var_type, column, name)
        self.__vars.append(new_var)
        return new_var

    def __getitem__(self, key):
        if (isinstance(key, str)):
            return self.__model.var_by_name(key)
        return self.__vars[key]

    def __len__(self) -> int:
        return len(self.__vars)

    def update_vars(self, n_vars: int):
        self.__vars = [Var(self.__model, i) for i in range(n_vars)]

    def remove(self, vars: List[Var]):
        iv = [1 for i in range(len(self.__vars))]
        vlist = [v.idx for v in vars]
        vlist.sort()
        for i in vlist:
            iv[i] = 0
        self.__model.solver.remove_vars(vlist)
        i = 0
        for v in self.__vars:
            if iv[v.idx] == 0:
                v.idx = -1
            else:
                v.idx = i
                i += 1
        self.__vars = [v for v in
                       self.__vars
                       if v.idx != -1]


# same as VarList but does not stores
# references for variables, used in
# callbacks
class VVarList(Sequence):

    def __init__(self, model: "Model", start: int = -1, end: int = -1):
        self.__model = model
        if start == -1:
            self.__start = 0
            self.__end = model.solver.num_cols()
        else:
            self.__start = start
            self.__end = end

    def add(self, name: str = "",
            lb: float = 0.0,
            ub: float = INF,
            obj: float = 0.0,
            var_type: str = CONTINUOUS,
            column: Column = None) -> Var:
        solver = self.__model.solver
        if not name:
            name = 'var({})'.format(len(self))
        if var_type == BINARY:
            lb = 0.0
            ub = 1.0
        new_var = Var(self.__model, solver.num_cols())
        solver.add_var(obj, lb, ub, var_type, column, name)
        return new_var

    def __getitem__(self, key):
        if (isinstance(key, str)):
            return self.__model.var_by_name(key)
        if (isinstance(key, slice)):
            return VVarList(self.__model, key.start, key.end)
        if (isinstance(key, int)):
            if key < 0:
                key = self.__end - key
            if key >= self.__end:
                raise IndexError

            return Var(self.__model, key + self.__start)

        raise Exception('Unknow type')

    def __len__(self) -> int:
        return self.__model.solver.num_cols()


class ConstrList(Sequence):
    """ List of problem constraints"""

    def __init__(self, model: "Model"):
        self.__model = model
        self.__constrs = []

    def __getitem__(self, key):
        if (isinstance(key, str)):
            return self.__model.constr_by_name(key)
        return self.__constrs[key]

    def add(self,
            lin_expr: LinExpr,
            name: str = '') -> Constr:
        if not name:
            name = 'constr({})'.format(len(self.__constrs))
        new_constr = Constr(self.__model, len(self.__constrs))
        self.__model.solver.add_constr(lin_expr, name)
        self.__constrs.append(new_constr)
        return new_constr

    def __len__(self) -> int:
        return len(self.__constrs)

    def remove(self, constrs: List[Constr]):
        iv = [1 for i in range(len(self.__constrs))]
        clist = [c.idx for c in constrs]
        clist.sort()
        for i in clist:
            iv[i] = 0
        self.__model.solver.remove_constrs(clist)
        i = 0
        for c in self.__constrs:
            if iv[c.idx] == 0:
                c.idx = -1
            else:
                c.idx = i
                i += 1
        self.__constrs = [c for c in
                          self.__constrs
                          if c.idx != -1]

    def update_constrs(self, n_constrs: int):
        self.__constrs = [Constr(self.__model, i) for i in range(n_constrs)]


# same as previous class, but does not stores
# anything and does not allows modification,
# used in callbacks
class VConstrList(Sequence):

    def __init__(self, model: "Model"):
        self.__model = model

    def __getitem__(self, key):
        if (isinstance(key, str)):
            return self.__model.constr_by_name(key)
        elif (isinstance(key, int)):
            return Constr(self.__model, key)
        elif (isinstance(key, slice)):
            return self[key]

        raise Exception('Use int or string as key')

    def __len__(self) -> int:
        return self.__model.solver.num_rows()
