from .Table import Table


class InputTable(Table):

    date_columns = []
    date_formats = {}

    def __init__(self, n_rows, n_cols, col_types, actual_table, col_names = None):
        return super().__init__(n_rows, n_cols, col_types, actual_table, col_names)

    def set_date_columns(self, date_columns):
        self.date_columns = date_columns

    def set_date_formats(self, date_formats):
        self.date_formats = date_formats

