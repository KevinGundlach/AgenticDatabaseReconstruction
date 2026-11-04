
class KeyReplaceError(Exception):
    pass 

def fill_measurement_objects(tree, paths, _current = ""):

    measurement_keys = ['value', 'min', 'max', 'unit', 'plus_minus']

    if isinstance(tree, list):
        
        for i in range(len(tree)):
            tree[i] = fill_measurement_objects(tree[i], paths, _current)

    elif isinstance(tree, dict):

        if _current in paths:
            for k in measurement_keys:
                tree.setdefault(k)

        for key, node in list(tree.items()):
            try:
                tree[key] = fill_measurement_objects(node, paths, _current + "." + key)
            except KeyReplaceError:
                suffix = type(tree[key]).__name__
                tree[key + "_" + suffix] = tree[key]
                del tree[key]

    elif _current in paths:

        if tree == 'balance':
            tree = {
                'value': -1.0,
                'min': None,
                'max': None,
                'unit': None,
                'plus_minus': None
            }

        elif isinstance(tree, str):
            raise KeyReplaceError() 

        elif isinstance(tree, int) or isinstance(tree, float):
            tree = {
                'value': float(tree),
                'min': None,
                'max': None,
                'unit': None,
                'plus_minus': None
            }

    return tree 
