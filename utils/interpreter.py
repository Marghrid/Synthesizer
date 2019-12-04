from tyrell.interpreter import PostOrderInterpreter, GeneralError
import rpy2.robjects as robjects
from tyrell.logger import get_logger
from utils.Table import Table
import os

counter_ = 0
logger = get_logger('tyrell')
tabs = {}

def get_collist(sel):
    sel_str = ",".join(sel)
    return "c(" + sel_str + ")"

def get_fresh_name():
    global counter_
    counter_ = counter_ + 1

    fresh_str = 'RET_DF_N' + str(counter_)
    return fresh_str

def get_fresh_col():
    global counter_
    counter_ = counter_ + 1

    fresh_str = 'COL' + str(counter_)
    return fresh_str

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


class RTransformer(PostOrderInterpreter):
    ## Concrete interpreter

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
        _script = '{ret_df} <- count({table})'.format(
                   ret_df=ret_df_name, table=args[0])
        return _script, ret_df_name

    def eval_select(self, node, args):

        if len(args[1]) == 1:
            args[1] = "(`" + args[1][0] + "`)"

        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- {table} %>% select(c{cols})'.format(
                   ret_df=ret_df_name, table=args[0], cols=args[1])
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            print(robjects.r(args[0]))
            print(_script)
            logger.error('Error in interpreting select...')
            raise GeneralError()

    def eval_filter(self, node, args):
        n_cols = robjects.r('ncol(' + args[0] + ')')[0]
        #self.assertArg(node, args,
        #        index=2,
        #        cond=lambda x: x <= n_cols,
        #        capture_indices=[0])

        ret_df_name = get_fresh_name()
        bor1 = "colnames({one})[{two}]".format(one=args[0], two=args[2])
        res1 = robjects.r(bor1)[0]
        _script = '{ret_df} <- {table} %>% filter({bor} {op} {const}) %>% droplevels()'.format(
                  ret_df=ret_df_name, table=args[0], bor=res1, op=args[1], col=str(args[2]), const=str(args[3]))

        return _script, ret_df_name

    def eval_separate(self, node, args):
        n_cols = robjects.r('ncol(' + args[0] + ')')[0]
        '''self.assertArg(node, args,
                index=1,
                cond=lambda x: x <= n_cols,
                capture_indices=[0])'''

        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- separate({table}, {col1}, c{into}, sep={char})'.format(
                  ret_df=ret_df_name, table=args[0], col1=str(args[1]), into=str(args[2]), char=str(args[3]), TMP1=get_fresh_col(), TMP2=get_fresh_col())
        try:
            ret_val = robjects.r(_script)
            #print(ret_val)
            tmp = build_tab(ret_df_name)
            for column in tmp.columns:
                if column.name in args[2]:
                    if column.type == 'float':
                        _script = '{table} <- transform({table}, {col} = as.numeric({col}))'.format(table=ret_df_name,
                                                                                                    col=column.name)
                        robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting separate...')
            raise GeneralError()

    def eval_spread(self, node, args):

        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- {table} %>% spread(\'{col1}\', \'{col2}\')'.format(
                  ret_df=ret_df_name, table=args[0], col1=str(args[1]), col2=str(args[2]))
        try:
            ret_val = robjects.r(_script)
            return ret_df_name
        except:
            logger.error('Error in interpreting spread...')
            raise GeneralError()

    def eval_group_by(self, node, args):
        cols = ''
        for i in args[1]:
            cols += str(i) + ','
        ret_df_name = get_fresh_name()
        _script = '{ret_df} <- group_by_at({table}, c({cols}))'.format(
                   ret_df=ret_df_name, table=args[0], cols=cols[:-1])

        return _script, ret_df_name

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

    def genarate_r(self, root):
        nodes = []
        prev = root
        found = 1
        while found != 0:
            found = 0
            nodes = [prev] + nodes
            for arg in prev._args:
                if str(type(arg)).find("ApplyNode") != -1:
                    prev = arg
                    found = 1
                    break

        _script = ""
        df = ""
        for node in nodes:
            fn = getattr(self, 'eval_' + node.name)
            args = []
            enter = 0
            for child in node._args:
                if str(type(child)).find("AtomNode") != -1:
                    args += [child.data]
                elif str(type(child)).find("ParamNode") != -1:
                    args += ['input0']
                    enter = 1
            if enter == 0: args = [df] + args
            part_script, df = fn(node, args)
            _script += "    " + part_script + os.linesep
        return _script
