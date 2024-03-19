import csv

class Db:
    def __init__(self, path):
        self.path = path

    def db_read(self):
        table = []
        with open(self.path, 'r', newline='') as file:
            reader = csv.reader(file)
            table = list(reader)
        return table

    def db_write(self, table):
        with open(self.path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(table)


