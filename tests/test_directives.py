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
