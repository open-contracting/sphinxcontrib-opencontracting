import re

import lxml.html
import pytest

from tests import path

def normalize(string):
    return re.sub(r'\n *', '', string)


@pytest.mark.sphinx(buildername='html', srcdir=path('field-description'), freshenv=True)
def test_field_description(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('field-description', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('field-description.html')) as f:
        expected = f.read()

    assert normalize(actual) == normalize(expected)


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description'), freshenv=True)
def test_code_description(app, status, warning):
    app.build()

    assert 'build succeeded' in status.getvalue()
    assert warning.getvalue().strip() == ''

    with open(path('code-description', '_build', 'html', 'index.html')) as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path('code-description.html')) as f:
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
