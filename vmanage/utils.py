def list_to_dict(lst, key_name, remove_key=True):
    """Convert a list of dictionaries into a dictionary of dictionaries.

    Args:
        key_name: The name of the key from the child dictionary to use to use in the parent.
        remove_key: Remove the key used for the parent dictionary from the child.


    Returns:
        result (dict): The resulting dictionary.

    """
    d = {}
    for item in lst:
        if key_name in item:
            if remove_key:
                key = item.pop(key_name)
            else:
                key = item[key_name]

            d[key] = item

    return d
