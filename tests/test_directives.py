import os
import re
from contextlib import contextmanager
from pathlib import Path

import lxml.html
import pytest
from sphinx.errors import ExtensionError

from sphinxcontrib.opencontracting import WORKEDEXAMPLE_ENV_ATTRIBUTE
from tests import path


def normalize(string):
    return re.sub(r'\n *', '', string)


def assert_build(app, status, warning, basename, messages=None):
    app.build()
    warnings = warning.getvalue().strip()

    with open(path(basename, '_build', 'html', 'index.html'), encoding='utf-8') as f:
        element = lxml.html.fromstring(f.read()).xpath('//div[@class="documentwrapper"]')[0]
        actual = lxml.html.tostring(element).decode()

    with open(path(f'{basename}.html'), encoding='utf-8') as f:
        expected = f.read()

    assert 'build succeeded' in status.getvalue()

    if messages:
        for message in messages:
            assert message in warnings
        assert len(messages) == len(warnings.split('\n'))
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


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionexplorerlinklist'), freshenv=True)
def test_extensionexplorerlinklist(app, status, warning):
    assert_build(app, status, warning, 'extensionexplorerlinklist')


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionexplorerlinklist'), freshenv=True,
                    confoverrides={'language': 'fr'})
def test_extensionexplorerlinklist_i18n(app, status, warning):
    assert_build(app, status, warning, 'extensionexplorerlinklist')


@pytest.mark.sphinx(buildername='html', srcdir=path('extensionlist'), freshenv=True)
def test_extensionlist(app, status, warning):
    assert_build(app, status, warning, 'extensionlist', [
        'WARNING: No extensions have category nonexistent in extensionlist directive',
    ])


@pytest.mark.skipif(os.name == 'nt', reason='Windows')
@pytest.mark.sphinx(buildername='html', srcdir=path('nonreadable'), freshenv=True)
def test_nonreadable(app, status, warning):
    basename = 'nonreadable'

    with nonreadable(path(basename, 'nonreadable.json')), nonreadable(path(basename, 'nonreadable.csv')):
        assert_build(app, status, warning, basename, [
            f"WARNING: JSON Schema file not readable: {path(basename, 'nonreadable.json')}",
            f"WARNING: CSV codelist file not readable: {path(basename, 'nonreadable.csv')}",
        ])


@pytest.mark.sphinx(buildername='html', srcdir=path('i18n'), freshenv=True,
                    confoverrides={'language': 'es'})
def test_i18n(app, status, warning):
    assert_build(app, status, warning, 'i18n')


@pytest.mark.sphinx(buildername='html', srcdir=path('i18n-missing-language'), freshenv=True,
                    confoverrides={'language': 'de'})
def test_i18n_missing_language(app, status, warning):
    assert_build(app, status, warning, 'i18n-missing-language', [
        "codelist_headers in conf.py is missing a 'de' key",
    ])


@pytest.mark.sphinx(buildername='html', srcdir=path('code-description-missing-column'), freshenv=True)
def test_code_description_missing_column(app, status, warning):
    basename = 'code-description-missing-column'

    assert_build(app, status, warning, basename, [
        f"Column 'non-code' not found (Code, Description): {path(basename, 'codelist.csv')}",
    ])


@pytest.mark.sphinx(buildername='html', srcdir=path('workedexample'), freshenv=True)
def test_workedexample(app, status, warning):
    env = app.builder.env
    assert not hasattr(env, WORKEDEXAMPLE_ENV_ATTRIBUTE)
    assert_build(app, status, warning, 'workedexample')
    assert getattr(env, WORKEDEXAMPLE_ENV_ATTRIBUTE)[0]['title'] == 'Unsuccessful tender'


@pytest.mark.sphinx(buildername='html', srcdir=path('workedexamplelist'), freshenv=True)
def test_workedexamplelist(app, status, warning):
    assert_build(app, status, warning, 'workedexamplelist')


@pytest.mark.sphinx(buildername='html', srcdir=path('workedexamplelist-non-existing'), freshenv=True)
def test_workedexamplelist_non_existing(app, status, warning):
    with pytest.raises(ExtensionError):
        assert_build(app, status, warning, 'workedexamplelist', [
            'WARNING: No worked examples are related to nonexistent',
        ])
