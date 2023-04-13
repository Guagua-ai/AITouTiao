def find_first_index(s: str, keys: list) -> int:
    ''' Find the first index of the key in the string '''
    first_index = -1
    key_found = None
    for key in keys:
        index = s.find(key)
        if index != -1 and (first_index == -1 or index < first_index):
            first_index = index
            key_found = key
            break
    return first_index + len(key_found) if key_found else -1
