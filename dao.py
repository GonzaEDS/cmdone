from helpers import separate_numbers, split_type
import re


class Dao:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        table = self.db.db_read()
        return table

    def append_item(self, item):
        table = self.db.db_read()
        table.append(item)
        self.db.db_write(table)
        return item

    def get_item(self, id):
        table = self.db.db_read()
        for item in table:
            if item[0] == id:
                return item
        return None

    def update_item(self, id, item):
        table = self.db.db_read()
        for i in range(len(table)):
            if table[i][0] == id:
                table[i] = item
                self.db.db_write(table)
                return item
        return None

    def delete_item(self, id):
        table = self.db.db_read()
        for i in range(len(table)):
            if table[i][0] == id:
                table.pop(i)
                self.db.db_write(table)

    def get_columns(self):
        table = self.db.db_read()
        return table[1]

    def get_column_names(self):
        table = self.db.db_read()
        column_names=[]
        for col in table[1]:
            name, _ = split_type(col)
            column_names.append(name)
        return column_names



    def get_first_row(self):
        table = self.db.db_read()
        return table[0][0]

    def get_last_id(self):
        table = self.db.db_read()
        if len(table) > 2:
            return table[-1][0]
        return None

    def get_ids(self):
        table = self.db.db_read()
        if len(table) > 2:
            return [i[0] for i in table[2:]]
        else:
            return []

    def new_id(self):
        table = self.db.db_read()
        if len(table) > 2:

            last_id = int(table[-1][0])
            return f"{last_id+1:02}"
        elif len(table) == 2:
            return '01'.zfill(2)

    def new_template_id(self):
        table = self.db.db_read()
        if len(table) > 2:
            last_id = table[-1][0]
            chars, nums = separate_numbers(last_id)
            return f"{chars}{int(nums)+1:02}"
        elif len(table) == 2:
            new_id = ''
            title_words = table[0][0].split(' ')
            for word in title_words:
                if re.search(r'\w', word[0]):
                    new_id += word[0].upper()
            new_id += '00'
            return new_id

        return None
