from bmt import Toolkit
import csv

t = Toolkit()
with open('debug_constants.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['name', 'is_predicate', 'inverse', 'ancestors'])
    for name in t.get_all_elements():
        row = [name, t.is_predicate(name)]
        if t.has_inverse(name):
            row.append(t.get_element(name).inverse)
        else:
            row.append(None)
        ancestors = t.get_ancestors(name)
        for ancestor in ancestors:
            if name != ancestor:
                row.append(ancestor)
        writer.writerow(row)
print('Done.')
