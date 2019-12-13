from typing import Any
from .from_iterator import FromIteratorEnumerator
from ..spec import *
from z3 import *
from collections import deque
from .. import dsl as D
from .optimizer import Optimizer
from copy import deepcopy
from ..decider import example_smt
from tyrell.logger import get_logger
from time import time

logger = get_logger('tyrell')
first = True


class BadSkeletonException(Exception):
    pass

class AST:

    def __init__(self):
        self.head = None
        self.tyrell_spec = None

    def dfs_dynamic(self, evaluator):
        return self.head.dfs_dynamic(self.tyrell_spec, evaluator)

    def dfs_fill(self):
        return self.head.dfs_fill(self.tyrell_spec)


class ASTNode:

    solver = None
    all_nodes = []

    def __init__(self, nb=None, depth=None, children=None):
        self.id = nb
        self.depth = depth
        self.children = children
        self.production = None
        self.parent = None
        ASTNode.all_nodes += [self]

    def dfs_dynamic(self, tyrell_spec: TyrellSpec, evaluator):
        if self.children is None or self.production.rhs == [0] or str(self.production).find("param") != -1:
            new_table = next(evaluator.eval(tyrell_spec, self.production))[0]
            yield [new_table], [[self.id, self.production]]
            return

        child = next(filter(lambda child: str(child.production).find('Table') != -1, self.children))
        gnrt = child.dfs_dynamic(tyrell_spec, evaluator)
        nxt1 = next(gnrt, None)
        while nxt1:
            tables, constants = nxt1
            new_gnrt = evaluator.eval(tyrell_spec, self.production, tables)
            nxt2 = next(new_gnrt, None)
            while nxt2:
                new_table, new_constants = nxt2
                yield [new_table], [[self.id] + [self.production] + constants + new_constants]
                nxt2 = next(new_gnrt, None)
            nxt1 = next(gnrt, None)

    def set_parent(self):
        if self.children is not None:
            for child in self.children:
                if child is not None:
                    child.parent = self
                    child.set_parent()

    def build_model(self, model):
        if str(self.production).find("Empty") == -1:
            model += [(self.id, self.production)]
        if self.children is not None:
            for child in self.children:
                model = child.build_model(model)
        return model

    def block_model(self, model):
        ctr = None
        for tup in model:
            if ctr is None:
                ctr = SmtEnumerator.enumerator.variables[tup[0] - 1] != WrapProduction.mapping[tup[1]].id
            else:
                ctr = Or(ctr, SmtEnumerator.enumerator.variables[tup[0] - 1] != WrapProduction.mapping[tup[1]].id)

        SmtEnumerator.enumerator.z3_solver.add(ctr)
        logger.debug("Learn " + str(ctr))
        SmtEnumerator.non_learned += 1
        raise BadSkeletonException


class WrapProduction:

    id = -1
    mapping = {}

    @staticmethod
    def get_id():
        WrapProduction.id += 1
        return WrapProduction.id

    def __init__(self, prod: Production):
        self.prod = prod
        self.id = self.get_id()
        self.constraints = {}
        WrapProduction.mapping[prod] = self

    def __repr__(self):
        return "{} {}: {}".format(WrapProduction.__name__, self.id, self.prod.__repr__())

    def __str__(self):
        return "{} {}: {}".format(WrapProduction.__name__, self.id, self.prod.__str__())

    def add(self, constraint):
        self.constraints = self.update_merge(self.constraints, constraint)

    def update_merge(self, d1, d2):
        if isinstance(d1, dict) and isinstance(d2, dict):
            # Unwrap d1 and d2 in new dictionary to keep non-shared keys with **d1, **d2
            # Next unwrap a dict that treats shared keys
            # If two keys have an equal value, we take that value as new value
            # If the values are not equal, we recursively merge them
            return {
                **d1, **d2,
                **{k: d1[k] if d1[k] == d2[k] else self.update_merge(d1[k], d2[k])
                   for k in {*d1} & {*d2}}
            }
        else:
            # This case happens when values are merged
            # It bundle values in a list, making sure
            # to flatten them if they are already lists
            return [
                *(d1 if isinstance(d1, list) else [d1]),
                *(d2 if isinstance(d2, list) else [d2])
            ]


class SmtEnumerator(FromIteratorEnumerator):
    skeleton_attempts = 0
    cuts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    properties = {'row': 0, 'col': 0, 'groups': 0, 'max': 0, 'min': 0, 'n_floats': 0, 'n_strings': 0, 'distinct': 0, 'biggest': 0, 'smallest': 0}
    enumerator = None
    learned = 0
    non_learned = 0
    time_on_sat = 0

    def __init__(self, tyrell_spec: TyrellSpec, depth: int, loc: int, evaluator):
        super().__init__(self.iterate())
        self.tyrell_spec = tyrell_spec
        self.depth = depth
        self.loc = loc
        self.productions = self.wrapProductions()
        self.max_children = self.maxChildren()
        self.tree, self.nodes = self.buildKTree(self.max_children, self.depth)
        self.evaluator = evaluator
        self.decider = None

        self.z3_solver = Solver()
        self.model = None
        self.variables = []
        self.variables_fun = []
        self.leaf_productions = []
        self.program2tree = {}
        self.buildRestrictions()
        self.optimizer = Optimizer(self.z3_solver, len(self.productions), self.variables, self.nodes)
        self.resolve_predicates()
        self.child_parent = {}
        self.constants_to_productions = {}
        SmtEnumerator.enumerator = self

    def set_decider(self, decider):
        self.decider = decider

    def wrapProductions(self):
        lst = []
        [lst.append(WrapProduction(prod)) for prod in self.tyrell_spec.get_productions_with_lhs(self.tyrell_spec.get_type("Empty"))]
        [lst.append(WrapProduction(prod)) for prod in self.tyrell_spec.get_productions_with_lhs(self.tyrell_spec.output)]
        return lst

    def maxChildren(self):
        '''Finds the maximum number of children in the high-order productions'''
        maximum = 0
        for p in self.productions:
            tmp = 0
            for val in p.prod.rhs:
                if val is self.tyrell_spec.output:
                    tmp += 1
            maximum = max(maximum, tmp)
        return maximum

    def buildKTree(self, children, depth):
        '''Builds a K-tree that will contain the program'''
        nodes = []
        tree = AST()
        root = ASTNode(1, 1)
        nb = 1
        tree.head = root
        d = deque()
        d.append(root)
        nodes.append(root)
        while len(d) != 0:
            current = d.popleft()
            current.children = []
            for x in range(0, children):
                nb += 1
                c = ASTNode(nb, current.depth + 1)
                nodes.append(c)
                current.children.append(c)
                if c.depth < depth:
                    d.append(c)
        root.set_parent()
        return tree, nodes

    def buildRestrictions(self):
        self.createInputProductions()
        self.createVariables()
        self.createLocConstraints()
        self.createInputConstraints()
        self.createFunctionConstraints()
        self.createLeafConstraints()
        self.createChildrenConstraints()
        self.allDifferent()

        #self.z3_solver.check()
        #self.model = self.z3_solver.model()
        #self.buildSkeleton()

    def createInputProductions(self):
        for p in self.productions:
            # FIXME: improve empty integration
            if not p.prod.is_function() or str(p.prod).find('Empty') != -1:
                self.leaf_productions.append(p)

    def createVariables(self):
        for x in range(0, len(self.nodes)):
            name = 'n' + str(x + 1)
            v = Int(name)
            self.variables.append(v)
            # variable range constraints
            self.z3_solver.add(And(v >= 0, v < len(self.productions)))
            hname = 'h' + str(x + 1)
            h = Int(hname)
            self.variables_fun.append(h)
            # high variables range constraints
            self.z3_solver.add(And(h >= 0, h <= 1))

    def createLocConstraints(self):
        '''Exactly k functions are used in the program'''
        ctr = self.variables_fun[0]
        for x in range(1, len(self.variables_fun)):
            ctr += self.variables_fun[x]
        ctr_fun = ctr == self.loc
        self.z3_solver.add(ctr_fun)

    def createInputConstraints(self):
        '''Each input will appear at least once in the program'''
        input_productions = []
        for prod1 in self.tyrell_spec.get_param_productions():
            for wrap_prod2 in self.productions:
                if prod1 == wrap_prod2.prod:
                    input_productions.append(wrap_prod2)

        for x in range(0, len(input_productions)):
            ctr = None
            for y in range(0, len(self.nodes)):
                if ctr is None:
                    ctr = self.variables[y] == input_productions[x].id
                else:
                    ctr = Or(self.variables[y] == input_productions[x].id, ctr)
            self.z3_solver.add(ctr)

    def createFunctionConstraints(self):
        '''If a function occurs then set the function variable to 1 and 0 otherwise'''
        assert len(self.nodes) == len(self.variables_fun)
        for x in range(0, len(self.nodes)):
            for p in self.productions:
                # FIXME: improve empty integration
                if p.prod.is_function() and str(p.prod).find('Empty') == -1:
                    ctr = Implies(
                        self.variables[x] == p.id, self.variables_fun[x] == 1)
                    self.z3_solver.add(ctr)
                else:
                    ctr = Implies(
                        self.variables[x] == p.id, self.variables_fun[x] == 0)
                    self.z3_solver.add(ctr)

    def createLeafConstraints(self):
        for x in range(0, len(self.nodes)):
            n = self.nodes[x]
            if n.children is None:
                ctr = self.variables[x] == self.leaf_productions[0].id
                for y in range(1, len(self.leaf_productions)):
                    ctr = Or(self.variables[x] ==
                             self.leaf_productions[y].id, ctr)
                self.z3_solver.add(ctr)

    def createChildrenConstraints(self):
        empty = None
        for p in self.productions:
            if str(p.prod).find('Empty') != -1:
                empty = p

        for x in range(0, len(self.nodes)):
            n = self.nodes[x]
            if n.children is not None:
                for p1 in self.productions:
                    assert len(n.children) > 0
                    maximum = 0
                    if p1.prod.is_function():
                        for value in p1.prod.rhs:
                            if value == self.tyrell_spec.output:
                                maximum += 1
                    for y in range(0, len(n.children)):
                        if p1.prod.is_function() and y < maximum:
                            ctr = None
                            for p2 in self.productions:
                                if str(p2.prod).find('Empty') == -1:
                                    if ctr is None:
                                        ctr = self.variables[n.children[y].id - 1] == p2.id
                                    else:
                                        ctr = Or(ctr, self.variables[n.children[y].id - 1] == p2.id)
                            self.z3_solver.add(Implies(self.variables[x] == p1.id, ctr))
                        else:
                            self.z3_solver.add(Implies(self.variables[x] == p1.id,
                                                       self.variables[n.children[y].id - 1] == empty.id))

    def allDifferent(self):
        empty = next(filter(lambda p: str(p).find('Empty') != -1, self.productions))
        empty_id = WrapProduction.id
        for i in range(len(self.variables)):
            var1 = self.variables[i]
            for j in range(i+1, len(self.variables)):
                var2 = self.variables[j]
                self.z3_solver.add(Implies(var1 == var2, var1 == empty_id))

    def blockModel(self):
        assert(self.model is not None)
        # m = self.z3_solver.model()
        block = []
        # block the model using only the variables that correspond to productions
        for x in self.variables:
            block.append(x != self.model[x])
        ctr = Or(block)
        self.z3_solver.add(ctr)

    def buildSkeleton(self):
        global first
        first = True
        SmtEnumerator.skeleton_attempts += 1
        result = [0] * len(self.model)
        for var in self.variables:
            result[(int(str(var)[1:])) - 1] = self.productions[int(self.model[var].as_long())].id
            #print(str(var), self.model[var])

        logger.debug("New Sketch")
        for n in self.nodes:
            prod = self.productions[result[n.id - 1]]
            #print(prod)
            n.production = prod.prod
            if str(prod).find("Empty") == -1:
                logger.debug(prod)

        self.tree.tyrell_spec = self.tyrell_spec
        programs = self.tree.dfs_dynamic(self.evaluator)
        program = next(programs, None)
        first = False
        while program is not None:
            builder = D.Builder(self.tyrell_spec)
            #[print(v) for v in self.program_to_linear(program[0])]
            #program[0]
            #input()
            self.program2tree.clear()
            self.decider.output_is(program[0][0])
            #print(self.program2tree)
            yield self.visit_this(program[1][0], builder)
            program = next(programs, None)


    def visit_this(self, lst, builder):
        children = []
        for el in lst[2:]:
            if isinstance(el, list):
                children += [self.visit_this(el, builder)]
            else:
                if el not in self.constants_to_productions:
                    self.constants_to_productions[el] = self.tyrell_spec.make_new_production(el)
                children += [builder.make_node(self.constants_to_productions[el], [])]

        ret = builder.make_node(lst[1], children)
        self.program2tree[ret] = lst[0]
        for child in children:
            self.child_parent[child] = ret
        return ret

    def program_to_linear(self, lst):
        lst = deepcopy(lst)
        i = 0
        while len(lst) > i:
            if isinstance(lst[i], list):
                head = lst[i][0]
                rest = lst[i][1:]
                lst += rest
                lst[i] = head
            i += 1
        return lst

    def block_program(self, program):
        return 0

    @staticmethod
    def _check_arg_types(pred, python_tys):
        if pred.num_args() < len(python_tys):
            msg = 'Predicate "{}" must have at least {} arugments. Only {} is found.'.format(
                pred.name, len(python_tys), pred.num_args())
            raise ValueError(msg)
        for index, (arg, python_ty) in enumerate(zip(pred.args, python_tys)):
            if not isinstance(arg, python_ty):
                msg = 'Argument {} of predicate {} has unexpected type.'.format(
                    index, pred.name)
                raise ValueError(msg)

    def _resolve_occurs_predicate(self, pred):
        self._check_arg_types(pred, [str, (int, float)])
        prod = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
        weight = pred.args[1]
        self.optimizer.mk_occurs(prod, weight)

    def _resolve_not_occurs_predicate(self, pred):
        self._check_arg_types(pred, [str, (int, float)])
        prod = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
        weight = pred.args[1]
        self.optimizer.mk_not_occurs(prod, weight)

    def _resolve_is_not_parent_predicate(self, pred):
        self._check_arg_types(pred, [str, str, (int, float)])
        prod0 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
        prod1 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[1])]
        weight = pred.args[2]
        self.optimizer.mk_is_not_parent(prod0, prod1, weight)

    def _resolve_is_parent_predicate(self, pred):
        self._check_arg_types(pred, [str, str, (int, float)])
        prod0 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
        prod1 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[1])]
        weight = pred.args[2]
        self.optimizer.mk_is_parent(prod0, prod1, weight)

    def _resolve_order_restriction(self, order_restrictions):
        for prod in order_restrictions:
            self.optimizer.mk_is_parent_subtree(prod, order_restrictions[prod])

    def _resolve_enforce_sequence(self, enforce_sequence):
        for prod in enforce_sequence:
            self.optimizer.mk_is_child(prod, enforce_sequence[prod])

    def _resolve_only_at_root(self, pred):
        prod0 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
        self.optimizer.mk_is_root(prod0)

    def resolve_predicates(self):
        try:
            order_restrictions = {}
            enforce_sequence = {}
            for pred in self.tyrell_spec.predicates():
                if pred.name == 'occurs':
                    self._resolve_occurs_predicate(pred)
                elif pred.name == 'is_parent':
                    self._resolve_is_parent_predicate(pred)
                elif pred.name == 'sequence':
                    prod0 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
                    prod1 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[1])]
                    if prod1 not in order_restrictions:
                        order_restrictions[prod1] = [prod0]
                    else:
                        order_restrictions[prod1] += [prod0]

                    if prod0 not in enforce_sequence:
                        enforce_sequence[prod0] = [prod1]
                    else:
                        enforce_sequence[prod0] += [prod1]

                elif pred.name == "order_restriction":
                    prod0 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[0])]
                    prod1 = WrapProduction.mapping[self.tyrell_spec.get_function_production_or_raise(pred.args[1])]
                    if prod0 not in enforce_sequence:
                        enforce_sequence[prod0] = [prod1]
                    else:
                        enforce_sequence[prod0] += [prod1]
                elif pred.name == "only_at_root":
                    self._resolve_only_at_root(pred)

            self._resolve_order_restriction(order_restrictions)
            self._resolve_enforce_sequence(enforce_sequence)
        except (KeyError, ValueError) as e:
            msg = 'Failed to resolve predicates. {}'.format(e)
            raise RuntimeError(msg) from None

    def iterate(self):

        while True:
            self.model = self.optimizer.optimize(self.z3_solver)
            try:
                #print(len(self.variables))
                #for var in self.variables:
                #    print(var, self.model[var], self.productions[int(self.model[var].as_long())])
                if self.model is not None:
                    skeleton = self.buildSkeleton()
                    concrete = next(skeleton, None)
                    concrete = self.test_concrete(concrete)
                    #yield concrete
                    #
                    while concrete is not None:
                        yield concrete
                        concrete = next(skeleton, None)
                        concrete = self.test_concrete(concrete)
                    self.blockModel()
                else:
                    return None
            except BadSkeletonException:
                logger.debug("Bad Sketch.")
                continue

    def test_concrete(self, concrete):
        self.z3_solver.push()
        ctr = None
        for var in self.variables:
            if ctr is None:
                ctr = var == self.model[var]
            else:
                ctr = And(ctr, var == self.model[var])
        self.z3_solver.add(ctr)
        if self.z3_solver.check() == unsat:
            concrete = None
        self.z3_solver.pop()
        return concrete

    def update(self, info: Any = None) -> None:
        # TODO: block more than one model
        #self.blockModel() # do I need to block the model anyway?
        if info is not None and not isinstance(info, str):
            for core in info:
                ctr = None
                for constraint in core:
                    x = self.variables[self.program2tree[constraint[0]] - 1]
                    y = WrapProduction.mapping[constraint[1]]
                    if ctr is None:
                        ctr = self.variables[self.program2tree[constraint[0]] - 1] \
                              != WrapProduction.mapping[constraint[1]].id
                    else:
                        ctr = Or(
                            ctr, self.variables[self.program2tree[constraint[0]] - 1]
                                 != WrapProduction.mapping[constraint[1]].id)
                self.z3_solver.add(ctr)
                SmtEnumerator.learned += 1

    def update_e(self, info = None):
        pass

    def prog_info(self):
        lst = []
        for variable in self.variables:
            if self.model[variable].as_long() > 0:
                lst += [(variable, self.model[variable])]
        return lst

    def info(self):
        #logger.debug(ASTNode.print())
        return "Number of Skeletons " + str(SmtEnumerator.skeleton_attempts) + os.linesep + \
               "Cuts level " + str(SmtEnumerator.cuts) + os.linesep + \
               "Properties " + str(SmtEnumerator.properties) + os.linesep + \
               "Learned {} things (NEO)".format(SmtEnumerator.learned) + os.linesep + \
               "Learned {} things (Non-NEO)".format(SmtEnumerator.non_learned) + os.linesep + \
               "Time spent on pruning {}".format(SmtEnumerator.time_on_sat)
