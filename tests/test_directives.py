import os
import re
from contextlib import contextmanager
from pathlib import Path

import lxml.html
import pytest

from tests import path


def normalize(string):
    return re.sub(r'\n *', '', string)


def assert_build(app, status, warning, basename, messages=None):
    app.build()
    warnings = warning.getvalue().strip()

    with open(path(basename, '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path(f'{basename}.html')) as f:
        expected = f.read()

    assert 'build succeeded' in status.getvalue()

    if messages:
        for message in messages:
            assert message in warnings
    else:
        assert warnings == ''

    assert normalize(actual) == normalize(expected)


@contextmanager
def nonreadable(filename):
    file = Path(filename)
    file.touch()
    file.chmod(0)
    try:
        yield
    finally:
        file.unlink()


@pytest.mark.sphinx(buildername='html', srcdir=path('field-description'), freshenv=True)
def test_field_description(app, status, warning):
    basename = 'field-description'

    assert_build(app, status, warning, basename, [
        f"WARNING: JSON Schema file not found: {path(basename, 'nonexistent.json')}",
        f"WARNING: JSON Schema file not valid: {path(basename, 'invalid.json')}",
        f"WARNING: Pointer '/properties/nonexistent/description' not found: {path(basename, 'schema.json')}",
    ])


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description'), freshenv=True)
def test_code_description(app, status, warning):
    basename = 'code-description'

    assert_build(app, status, warning, basename, [
        f"WARNING: CSV codelist file not found: {path(basename, 'nonexistent.csv')}",
        f"WARNING: Value 'nonexistent' not found in column 'Code': {path(basename, 'codelist.csv')}",
    ])


@pytest.mark.skipif(os.name == 'nt', reason='Windows')
@pytest.mark.sphinx(buildername='html', srcdir=path('basic'), freshenv=True)
def test_field_description_nonreadable(app, status, warning):
    basename = 'basic'

    with nonreadable(path(basename, 'nonreadable.json')):
        assert_build(app, status, warning, basename, [
            f"WARNING: JSON Schema file not readable: {path(basename, 'nonreadable.json')}"
        ])


@pytest.mark.skipif(os.name == 'nt', reason='Windows')
@pytest.mark.sphinx(buildername='html', srcdir=path('basic'), freshenv=True)
def test_code_description_nonreadable(app, status, warning):
    basename = 'basic'

    with nonreadable(path(basename, 'nonreadable.csv')):
        assert_build(app, status, warning, basename, [
            f"WARNING: CSV codelist file not readable: {path(basename, 'nonreadable.csv')}"
        ])


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description-i18n'), freshenv=True,
                    confoverrides={'language': 'es'})
def test_code_description_i18n(app, status, warning):
    assert_build(app, status, warning, 'code-description-i18n')


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description-column'), freshenv=True)
def test_code_description_column(app, status, warning):
    basename = 'code-description-column'

    assert_build(app, status, warning, basename, [
        f"Column 'non-code' not found (Code, Description): {path(basename, 'codelist.csv')}"
    ])


@pytest.mark.sphinx(buildername='html', srcdir=path('codelisttable'), freshenv=True)
def test_codelisttable(app, status, warning):
    assert_build(app, status, warning, 'codelisttable')


@pytest.mark.sphinx(buildername='html', srcdir=path('codelisttable-i18n'), freshenv=True,
                    confoverrides={'language': 'es'})
def test_codelisttable_i18n(app, status, warning):
    assert_build(app, status, warning, 'codelisttable-i18n')


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionexplorerlinklist'), freshenv=True)
def test_extensionexplorerlinklist(app, status, warning):
    assert_build(app, status, warning, 'extensionexplorerlinklist')


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionlist'), freshenv=True)
def test_extensionlist(app, status, warning):
    assert_build(app, status, warning, 'extensionlist', [
        'WARNING: No extensions have category nonexistent in extensionlist directive',
    ])
