import os.path


def path(*args):
    return os.path.join(os.path.dirname(os.path.realpath(__file__), 'fixtures', *args))
