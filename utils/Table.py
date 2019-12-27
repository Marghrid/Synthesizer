import os
import numpy as np
import pandas
import copy
from numpy import linalg as LA
import math
import random

class Table:
    # Statistics
    structure = 0
    elements = 0
    types = 0
    last_norm = 0
    statistics = {"cols_avg": 0, "cols_max": 0, "cols": 0}

    def __init__(self, n_rows, n_cols, col_types, actual_table, col_names = None):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.col_types = col_types
        self.columns = []
        self.max_input = 0
        if actual_table is None:
            self.parse2(col_types, col_names)
        else:
            self.parse(col_types, actual_table)

    def parse(self, col_types, csv_table):
        rows = csv_table.split(os.linesep)
        col_names = rows[0].split(',')
        rows = rows[1:-1]
        for i in range(self.n_cols):
            col = Column(col_types[i], col_names[i], i+1)
            for row in rows:
                try:
                    col.append(row.split(',')[i])
                except:
                    continue
            col.eval_elements()
            self.col_types[i] = col.type
            self.columns += [col]

    def parse2(self, col_types, col_names):
        col_names = col_names
        for i in range(self.n_cols):
            col = Column(col_types[i], col_names[i], i+1)
            self.col_types[i] = col.type
            self.columns += [col]


    def is_key_value(self, key_index, value_index):
        for key in list(set(self.columns[key_index].values)):
            rows = [i for i in range(self.n_rows) if self.columns[key_index].values[i] == key]
            all_rows = []
            for row in rows:
                row_content = []
                for col_n in range(self.n_cols):
                    if col_n != value_index:
                        row_content += [self.columns[col_n].values[row]]
                if row_content in all_rows:
                    return False
                all_rows += [row_content]
        return True

    def get_cols_by_type(self):
        floats = [i for i in range(self.n_cols) if self.columns[i].type == "float"]
        strings = [i for i in range(self.n_cols) if self.columns[i].type == "string"]
        return floats, strings

    def equals(self, other):
        other = copy.deepcopy(other)
        if not isinstance(other, Table):
            return False
        # Compare the number of rows and columns
        if self.n_rows != other.n_rows or \
            self.n_cols != other.n_cols:
            Table.structure += 1
            return False

        # Compare types
        if sorted(self.col_types) != sorted(other.col_types):
            Table.types +=1
            return False

        # Match each column accordingly (we assume relation between values are preserved)
        other_columns = other.columns
        self_columns = self.columns
        for col1 in self_columns:
            match = False
            for col2 in other_columns:
                if col1.matches(col2):
                    match = True
                    other_columns.remove(col2)
                    break

                Table.statistics['cols'] += 1
                Table.statistics['cols_avg'] = Table.statistics['cols_avg'] + (col1.norm - Table.statistics['cols_avg']) / Table.statistics['cols']
                Table.statistics['cols_max'] = max(Table.statistics['cols_max'], col1.norm)
            Table.statistics['cols'] += 1
            Table.statistics['cols_avg'] = Table.statistics['cols_avg'] + (
                        col1.norm - Table.statistics['cols_avg']) / Table.statistics['cols']
            Table.statistics['cols_max'] = max(Table.statistics['cols_max'], col1.norm)
            if not match:
                Table.elements += 1
                return False

        #print('Structure', Table.structure)
        #print('Types', Table.types)
        #print('Elements', Table.elements)
        return True


    def __eq__(self, other):
        other = copy.deepcopy(other)
        if not isinstance(other, Table):
            return False
        # Compare the number of rows and columns
        if self.n_rows != other.n_rows or \
            self.n_cols != other.n_cols:
            return False

        # Compare types
        #if sorted(self.col_types) != sorted(other.col_types):
        #    return False

        # Match each column accordingly (we assume relation between values are preserved)
        other_column = other.columns[1]
        self_column = self.columns[1]

        if other_column.matches(self_column, other.max_input) or (other_column.values == [] and self_column == []):
            Table.last_norm = other_column.norm
            return True
        return False


    def maximum(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "float"]
        maximum = 0
        for col in cols:
            maximum = max(self.columns[col].values + [maximum])
        return maximum

    def minimum(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "float"]
        minimum = 1_000_000
        for col in cols:
            minimum = min(self.columns[col].values + [minimum])
        return minimum

    def distinct(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "string"]
        tmp = set()
        for col in cols:
            [tmp.add(val) for val in self.columns[col].values]
        return len(tmp)

    def smallest_string(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "string"]
        minimum = 1_000_000
        for col in cols:
            minimum = min([len(val) for val in self.columns[col].values] + [minimum])
        return minimum

    def biggest_string(self):
        cols = [i for i in range(len(self.col_types)) if self.col_types[i] == "string"]
        maximum = 0
        for col in cols:
            maximum = max([len(val) for val in self.columns[col].values] + [maximum])
        return maximum

    @staticmethod
    def info():
        string = 'Structure ' + str(Table.structure) + os.linesep
        string += 'Types ' + str(Table.types) + os.linesep
        string += 'Elements '+ str(Table.elements) + os.linesep
        string += 'Column average distance ' + str(Table.statistics['cols_avg']) + ' for ' + str(Table.statistics['cols']) + ' columns' + os.linesep
        string += 'Column max ' + str(Table.statistics['cols_max'])
        return string

    def __str__(self):
        out = ''
        for col in self.columns:
            out += str(col) + os.linesep
        return out[:-1]

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

    def add_noise(self):
        for column in self.columns:
            column.add_noise()

class Column:
    def __init__(self, type, name, n):
        self.type = type
        self.name = name
        self.values = []
        self.n = n
        self.norm = 0

    def append(self, value):
        self.values += [value]

    def contains(self, item):
        lst = [str(val).count(item) for val in self.values]
        if lst == []:
            i = 0
        return min(lst)

    def matches(self, other, maximum):
        if self.type == "float" or self.type == "numeric":
            if other.type == "float" or self.type == "numeric":
                a1 = np.array(self.values)
                a2 = np.array(other.values)
                self.norm = LA.norm(np.subtract(a1/maximum, a2/maximum), ord=1)
                return self.norm <= 0.15 * len(a1)
            else:
                self.norm = 0
                return False
        else:
            self.norm = 0
            return False

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

    def __str__(self):
        return self.type + ' ' + str(self.values)

    def add_noise(self):
        if self.type == "float":
            maximum = max(self.values)
            for i in range(len(self.values)):
                if random.randint(0, 1) == 0:
                    self.values[i] += maximum * (random.randrange(0, 10)) * 0.01
                else:
                    self.values[i] -= maximum * (random.randrange(0, 10)) * 0.01



def test():
    x = Table(4, 2, ["int", "string"], '''id,name
    2,"bla x"
    3,ble
    4,blo
    5,blu
    ''')

    y = Table(4, 2, ["string", "int"], '''name,id
    5,blu
    2,"bla x"
    4,blo,
    3,ble
    ''')

    print(x)
    print(y)

    print(x==y)
