from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def chunk_list(input_list, chunk_size):
    if len(input_list) < chunk_size:
        return [input_list]
    chunked_list = [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
    return chunked_list


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1', True):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0', False):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def remove_none_values(params):
    return {k: v for k, v in params.items() if v is not None}
