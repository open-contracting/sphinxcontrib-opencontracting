import os
import re
from contextlib import contextmanager
from pathlib import Path

import lxml.html
import pytest

from tests import path


def normalize(string):
    return re.sub(r'\n *', '', string)


@contextmanager
def nonreadable(filename):
    file = Path(filename)
    file.touch()
    file.chmod(0)
    try:
        yield
    finally:
        file.chmod(700)
        file.unlink()


@pytest.mark.sphinx(buildername='html', srcdir=path('field-description'), freshenv=True)
def test_field_description(app, status, warning):
    with nonreadable(path('field-description', 'nonreadable.json')):
        app.build()
        warnings = warning.getvalue().strip()

        not_found = f"WARNING: JSON Schema file not found: {path('field-description', 'nonexistent.json')}"
        not_readable = f"WARNING: JSON Schema file not readable: {path('field-description', 'nonreadable.json')}"

        assert 'build succeeded' in status.getvalue()
        assert not_found in warnings
        assert not_readable in warnings or os.name != 'nt'

        with open(path('field-description', '_build', 'html', 'index.html')) as f:
            element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
            actual = lxml.html.tostring(element).decode()

        with open(path('field-description.html')) as f:
            expected = f.read()

        assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description'), freshenv=True)
def test_code_description(app, status, warning):
    with nonreadable(path('code-description', 'nonreadable.csv')):
        app.build()
        warnings = warning.getvalue().strip()

        not_found = f"WARNING: CSV codelist file not found: {path('code-description', 'nonexistent.csv')}"
        not_readable = f"WARNING: CSV codelist file not readable: {path('code-description', 'nonreadable.csv')}"

        assert 'build succeeded' in status.getvalue()
        assert not_found in warnings
        assert not_readable in warnings or os.name != 'nt'

        with open(path('code-description', '_build', 'html', 'index.html')) as f:
            element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
            actual = lxml.html.tostring(element).decode()

        with open(path('code-description.html')) as f:
            expected = f.read()

        assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description-i18n'), freshenv=True,
                    confoverrides={'language': 'es'})
def test_code_description_i18n(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('code-description-i18n', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('code-description-i18n.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('codelisttable'), freshenv=True)
def test_codelisttable(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('codelisttable', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('codelisttable.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('codelisttable-i18n'), freshenv=True,
                    confoverrides={'language': 'es'})
def test_codelisttable_i18n(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('codelisttable-i18n', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('codelisttable-i18n.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionexplorerlinklist'), freshenv=True)
def test_extensionexplorerlinklist(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('extensionexplorerlinklist', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('extensionexplorerlinklist.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionlist'), freshenv=True)
def test_extensionlist(app, status, warning):
    app.build()
    message = 'WARNING: No extensions have category nonexistent in extensionlist directive'

    assert 'build succeeded' in status.getvalue()
    assert message in warning.getvalue().strip()

    with open(path('extensionlist', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('extensionlist.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)
