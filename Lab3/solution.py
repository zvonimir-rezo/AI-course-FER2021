import csv
import sys


class Node:
    def __init__(self, value, children, parent):
        self.value = value
        self.children = children
        self.parent = parent


class ID3:
    def __init__(self, d, d_parent, X, y):
        self.d = d
        self.d_parent = d_parent
        self.X = X
        self.y = y

    def fit(self, data):
        if not self.d:
            v = max(self.d_parent)

    def predict(self, data):
        pass


def entropy():
    pass


def main():
    csv_file = sys.argv[0]
    with open('C:\\Users\\Zvone\\Desktop\\UI_lab\\Lab3\\lab3_files\\datasets\\heldout_logic_f2_test.csv', newline="\n") as csvfile:
        reader = csv.reader(csvfile)
        rows = []
        for row in reader:
            rows.append(row)
        header = rows[0]
        dependent_var = header[len(header-1)]
        rows2 = rows

    id3 = ID3(rows[1:], rows2[1:], header, dependent_var)


main()