#!/usr/bin/env python

import tyrell.spec as S
from tyrell.interpreter import PostOrderInterpreter, GeneralError
from tyrell.enumerator import SmtEnumerator
from tyrell.decider import Example, SmtBasicDecider
from tyrell.synthesizer import Synthesizer
from tyrell.logger import get_logger
import rpy2.robjects as robjects
import argparse
from utils.Table import Table
import os, signal
import itertools
import sys
import math
from utils.interpreter import RTransformer


logger = get_logger('tyrell')
number = 0
counter_ = 1
tabs = {}
inc_tabs = {}
robjects.r('''
    library(dplyr)
    library(tidyr)
    library(tibble)
    library(compare)
   ''')

## Common utils.
def get_collist(sel):
    sel_str = ",".join(sel)
    return "c(" + sel_str + ")"

def get_fresh_name():
    global counter_
    counter_ = counter_ + 1

    fresh_str = 'RET_DF' + str(counter_)
    return fresh_str

def get_fresh_col():
    global counter_ 
    counter_ = counter_ + 1

    fresh_str = 'COL' + str(counter_)
    return fresh_str

def get_type(df, index):
    _rscript = 'sapply({df_name}, class)[{pos}]'.format(df_name=df, pos=index)
    ret_val = robjects.r(_rscript)
    return ret_val[0]

def quotezise(string):
    return "'" + string + "'"


def eq_r(actual, expect):
    if build_incomplete_tab(actual) != build_incomplete_tab(expect):
        return False
    tab1 = build_tab(actual)
    tab2 = build_tab(expect)
    """if tab1 == tab2:
        logger.info(tab1)
        logger.info(tab2)"""
    return tab1 == tab2


def build_incomplete_tab(name):
    if name in inc_tabs:
        return inc_tabs[name]
    n_cols = robjects.r('ncol(' + name + ')')[0]
    n_rows = robjects.r('nrow(' + name + ')')[0]
    col_types = [robjects.r('sapply(' + name + ', class)')[i] for i in range(n_cols)]
    col_names = [robjects.r('colnames(' + name + ')')[i] for i in range(n_cols)]
    inc_tabs[name] = Table(n_rows, n_cols, col_types, None, col_names)
    return inc_tabs[name]


def build_tab(name):
    if name in tabs:
        return tabs[name]

    tab = robjects.r(
        '''capture.output(write.table({lhs}, row.names=FALSE,col.names=TRUE, sep=",", quote=FALSE))'''.format(
            lhs=name))
    lines = tab.items()
    line = next(lines, None)
    csv = ''
    while line:
        csv += line[1] + os.linesep
        line = next(lines, None)
    n_cols = robjects.r('ncol(' + name + ')')[0]
    n_rows = robjects.r('nrow(' + name + ')')[0]
    col_types = [robjects.r('sapply(' + name + ', class)')[i] for i in range(n_cols)]
    tabs[name] = Table(n_rows, n_cols, col_types, csv)
    return tabs[name]


class RInterpreter(PostOrderInterpreter):

    def eval_group_vars(self, table):
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- group_vars({table})'.format(
            ret_df=ret_df_name, table=table)
        try:
            ret_val = robjects.r(_script)
            return ret_val
        except:
            logger.error('Error in interpreting rowid_to_table...')
            raise GeneralError()


    def eval_rowid_to_column(self, table):
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- rowid_to_column({table})'.format(
            ret_df=ret_df_name, table=table)
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting rowid_to_table...')
            raise GeneralError()

    def eval_colname(self, table, index):
        bor1 = "colnames({one})[{two}]".format(one=table, two=index)
        res1 = robjects.r(bor1)[0]
        return res1

    def eval_ncols(self, table):
        return robjects.r('ncol(' + table + ')')[0]

    def eval_const(self, node, args=[]):
        if not args:
            args = [node]
        return args[0]

    def eval_count(self, node, args):
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- summarize({table}, n=n())\n' \
                  '{ret_df}$n <- as.numeric({ret_df}$n)'.format(
                   ret_df=ret_df_name, table=args[0])
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting count...')
            raise GeneralError()

    def eval_group_by(self, node, args):
        cols = ''
        for i in args[1]:
            cols += str(i) + ','
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- group_by_at({table}, c({cols}))'.format(
                   ret_df=ret_df_name, table=args[0], cols=cols[:-1])
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting group_by...')
            raise GeneralError()

    def eval_summarise(self, node, args):
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- {table} %>% summarise_at(.vars = colnames(.)[{col}], {aggr})'.format(
                  ret_df=ret_df_name, table=args[0], aggr=str(args[1]), col=str(args[2]))
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.info(robjects.r(args[0]))
            logger.error('Error in interpreting summarise...')
            raise GeneralError()


    def eval_mutate(self, node, args):
        if args[3]:
            cols = ""
            for tmp in args[3]:
                cols += tmp + ","
            args[3] = "c(" + cols[:-1] + ")"
        else:
            args[3] = ""
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- {table} %>% mutate(`{res}`={op}({cols}))'.format(
                  ret_df=ret_df_name, table=args[0], res=args[1], op=args[2], cols=args[3])

        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting mutate...')
            raise GeneralError()

    def eval_top_n(self, node, args):
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- {table} %>% top_n({number}, {col}) %>% arrange(desc({col}))'.format(
                  ret_df=ret_df_name, table=args[0], number=args[1], col=args[2])
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting top_n...')
            raise GeneralError()


    def apply_row(self, val):
        df = val
        if isinstance(val, str):
            df = robjects.r(val)
        return df.nrow

    def apply_col(self, val):
        df = val
        if isinstance(val, str):
            df = robjects.r(val)
        return df.ncol

    def apply_groups(self, val):
        df = val
        if isinstance(val, str):
            if robjects.r("is.grouped_df({})".format(df))[0]:
                return robjects.r(self.eval_count(None, [df])).nrow
            else:
                return robjects.r(df).nrow


def init_tbl(df_name, csv_loc):
    cmd = '''
    tbl_name <- read.csv(csv_location, check.names = FALSE)
    fctr.cols <- sapply(tbl_name, is.factor)
    int.cols <- sapply(tbl_name, is.integer)
    tbl_name[, fctr.cols] <- sapply(tbl_name[, fctr.cols], as.character)
    tbl_name[, int.cols] <- sapply(tbl_name[, int.cols], as.numeric)
    '''
    cmd = cmd.replace('tbl_name', df_name).replace('csv_location', '"'+ csv_loc + '"')
    robjects.r(cmd)
    return None


class Evaluator:

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.context = []

    def eval(self, tyrell_spec, prod, tables=None):
        try:
            gn = self.evaluate(tyrell_spec, prod, tables)
            nxt = next(gn, None)
            while nxt:
                yield nxt
                nxt = next(gn, None)
        except:
            return

    def evaluate(self, tyrell_spec, prod, tables=None):

        if str(prod).find("param") != -1:
            yield 'input' + str(prod._param_id), []
        else:
            table = tables[0]
            tab = build_incomplete_tab(tables[0])
            if tab.n_rows == 0 or tab.n_cols == 0:
                return
            elif str(prod).find("group_by") != -1:
                n_cols = tab.n_cols
                cols = [i for i in range(n_cols)]
                for i in range(1, min(n_cols+1, 2)):
                    for combination in itertools.combinations(cols, i):
                        cnsts = [tuple([c + 1 for c in combination])]
                        res = self.interpreter.eval_group_by(None, [table] + cnsts)
                        if self.interpreter.apply_groups(res) != self.interpreter.apply_groups(table):
                            yield res, cnsts
            elif str(prod).find("summarise") != -1:
                n_cols = tab.n_cols
                group_vars = self.interpreter.eval_group_vars(table)
                group_vars = list(group_vars)
                for i in range(n_cols):
                    if tab.columns[i].type == "numeric" and tab.columns[i].name not in group_vars:
                        for op in ["max", "min", "mean", "sum", "median"]:
                            res = self.interpreter.eval_summarise(None, [table, op, i+1])
                            yield res, [op, i+1]
            elif str(prod).find("count") != -1:
                yield self.interpreter.eval_count(None, [table]), []
            elif str(prod).find("mutate") != -1:
                group_vars = self.interpreter.eval_group_vars(table)
                group_vars = list(group_vars)
                colindexes = [i for i in range(tab.n_cols) if tab.columns[i].type == "numeric" and tab.columns[i].name not in group_vars]
                for i in range(1, min(len(colindexes) + 1, 2)):
                    for combination in itertools.combinations(colindexes, i):
                        for op in ["cumsum"]:
                            cnsts = [get_fresh_col(), op, tuple([tab.columns[c].name for c in combination])]
                            res = self.interpreter.eval_mutate(None, [table] + cnsts)
                            yield res, cnsts
                        #custom functions
                        for op in ["normalit"]:
                            cnsts = [[tab.columns[c].name for c in combination][0], op, tuple([tab.columns[c].name for c in combination])]
                            res = self.interpreter.eval_mutate(None, [table] + cnsts)
                            yield res, cnsts
                for i in range(1, min(len(colindexes) + 1, 4)):
                    for combination in itertools.combinations(colindexes, i):
                        for op in ["max", "sum", "mean", "min", "median"]:
                            cnsts = [get_fresh_col(), op, tuple([tab.columns[c].name for c in combination])]
                            res = self.interpreter.eval_mutate(None, [table] + cnsts)
                            yield res, cnsts
                for op in ["n"]:
                    cnsts = [get_fresh_col(), op, tuple()]
                    res = self.interpreter.eval_mutate(None, [table] + cnsts)
                    yield res, cnsts
            elif str(prod).find("top_n") != -1:
                for i in range(tab.n_cols):
                    if tab.columns[i].type == "numeric":
                        for j in range(min(12, tab.n_rows), 9, -1):
                            cnsts = [j, tab.columns[i].name]
                            res = self.interpreter.eval_top_n(None, [table] + cnsts)
                            yield res, cnsts


    def eval_rows(self, table):
        return self.interpreter.apply_row(table)

    def eval_cols(self, table):
        return self.interpreter.apply_col(table)

    def eval_groups(self, table):
        return self.interpreter.apply_groups(table)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i0', '--input0', type=str)
    parser.add_argument('-o', '--output', type=str)
    parser.add_argument('-l', '--length', type=int)
    parser.add_argument('-d', '--depth', type=int)
    parser.add_argument('-t', '--tyrellpath', type=str)
    parser.add_argument('-m', '--plotmax', type=float)
    args = parser.parse_args()
    loc_val = args.length
    depth = args.depth
    # Input and Output must be in CSV format.
    input0 = args.input0
    output = args.output

    # This is required by Ruben.
    init_tbl('input0', input0)
    init_tbl('output', output)
    build_tab('output').max_input = args.plotmax

    logger.info('Parsing Spec...')
    spec = S.parse_file(args.tyrellpath)
    logger.info('Parsing succeeded')

    logger.info('Building synthesizer...')
    r_interpreter = RInterpreter()

    synthesizer = Synthesizer(
        #loc: # of function productions
        # enumerator=SmtEnumerator(spec, depth=2, loc=1),
        # enumerator=SmtEnumerator(spec, depth=3, loc=2),

        enumerator=SmtEnumerator(spec, depth=depth, loc=loc_val, evaluator=Evaluator(r_interpreter)),
        decider=SmtBasicDecider(
            spec=spec,
            interpreter=r_interpreter,
            examples=[
                # Example(input=[DataFrame2(benchmark1_input)], output=benchmark1_output),
                Example(input=['input0'], output='output'),
            ],
            equal_output=eq_r
        )
    )
    logger.info('Synthesizing programs...')
    synthesizer.set_table(Table)
    prog = synthesizer.synthesize()
    if prog is not None:
        logger.info('Solution found: {}'.format(prog))
    else:
        logger.info('Solution not found!')
    sys.stderr.flush()


if __name__ == '__main__':
    logger.setLevel('INFO')
    main()

