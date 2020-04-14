def list_to_dict(lst, key_name, remove_key=True):
    d = {}
    for item in lst:
        if key_name in item:
            if remove_key:
                key = item.pop(key_name)
            else:
                key = item[key_name]

            d[key] = item

    return d
