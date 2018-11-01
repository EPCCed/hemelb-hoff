def queryresult_to_array(keys, queryresult):

    d = []
    try:
        for q in queryresult:
            row = {}
            for k in keys:
                row[k] = getattr(q, k)
            d.append(row)
    except TypeError:
        row = {}
        for k in keys:
            row[k] = getattr(queryresult, k)
        d.append(row)
    return d

def queryresult_to_dict(keys, queryresult):

    d = {}
    try:
        for q in queryresult:
            row = {}
            for k in keys:
                row[k] = getattr(q, k)
            d.update(row)
    except TypeError:
        row = {}
        for k in keys:
            row[k] = getattr(queryresult, k)
        d.update(row)
    return d