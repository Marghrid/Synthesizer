import rpy2.robjects as robjects
import argparse
import os
import numpy as np
import copy
from numpy import linalg as LA
import math
import random

class Table:
    def __init__(self, n_rows, n_cols, col_types, actual_table):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.col_types = col_types
        self.columns = []
        self.parse(col_types, actual_table)

    def parse(self, col_types, csv_table):
        rows = csv_table.split(os.linesep)
        col_names = rows[0].split(',')
        rows = rows[1:-1]
        for i in range(self.n_cols):
            col = Column(col_types[i], col_names[i], i+1)
            for row in rows:
                col.append(row.split(',')[i])
            col.eval_elements()
            self.col_types[i] = col.type
            self.columns += [col]

    def csv(self):
        out = ''
        for i in range(self.n_cols):
            out += "col{}".format(i) + ","
        out = out[:-1] + "\n"
        line = ""
        for n in range(self.n_rows):
            for col in self.columns:
                line += str(col.values[n]) + ","
            out += line[:-1] + "\n"
            line = ""
        return out

    def maximum(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "float"]
        maximum = 0
        for col in cols:
            maximum = max(self.columns[col].values + [maximum])
        return math.ceil(maximum*1.20)

    def template():
        return '''
\\begin{tikzpicture}
    \\centering
        \\begin{axis}[
            ybar, axis on top, height=8.5cm, width=13cm, bar width=0.6cm,
            ymax = ymax_decide,
            ymin = 0,
            ylabel style={align=center},
            symbolic x coords={col1_fill_symbols},
            xtick=data,
            x tick label style={font=\\small,text width=1cm,align=center},
            legend style={at={(0.5,-0.1.5)},
                    anchor=north,legend columns=-1},
            ]
            \\addplot coordinates {
col2_fill
            };
        \\end{axis}
    \\label{fig:example}
\\end{tikzpicture}'''


class Column:
    def __init__(self, type, name, n):
        self.type = type
        self.name = name
        self.values = []
        self.n = n
        self.norm = 0

    def append(self, value):
        self.values += [value]

    def eval_elements(self):
        try:
            if len(self.values) > 0 and str(self.values[0]).find("_") != - 1:
                self.type = "string"
                return
            tmp = list(map(float, self.values))
            self.values = tmp
            self.type = "float"
        except ValueError:
            self.type = "string"


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

def build_tab(name):

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
    return Table(n_rows, n_cols, col_types, csv)



if __name__ == "__main__":

    robjects.r('''
        library(dplyr)
        library(tidyr)
        library(tibble)
    ''')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i0', '--input0', type=str)
    args = parser.parse_args()
    input0 = args.input0
    init_tbl('input0', input0)
    program = '''
    RET_DF_N1 <- input0 %>% filter(To == "LIS") %>% droplevels()
    RET_DF_N2 <- group_by_at(RET_DF_N1, c(2))
    RET_DF_N3 <- count(RET_DF_N2)

    '''
    robjects.r(program)
    output_table = build_tab('RET_DF_N3')

    str_col = output_table.columns[0]
    float_col = output_table.columns[1]
    if str_col.type != "string":
        str_col = output_table.columns[1]
        float_col = output_table.columns[0]

    coordinates = ""
    symbolic = ""
    for i in range(len(float_col.values)):
        coordinates += "               ("+str(str_col.values[i])+ ", " + str(float_col.values[i]) + ")" + os.linesep
        symbolic += str_col.values[i] + ","
    template = Table.template()
    template = template.replace('col2_fill', coordinates[:-1])
    template = template.replace('col1_fill_symbols', symbolic[:-1])
    template = template.replace('ymax_decide', str(int(output_table.maximum())))
    print(template)
