from pathlib import Path


def path(*args):
    return Path(__file__).resolve().parent.joinpath("fixtures", *args)
