from os.path import dirname, abspath

from django.apps import apps


def load_tests(loader, tests, pattern):
    if apps.is_installed("tapir.shifts"):
        # Actually load the tests - thanks to @barney-szabolcs
        return loader.discover(start_dir=dirname(abspath(__file__)), pattern=pattern)
