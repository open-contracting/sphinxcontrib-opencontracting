from setuptools import setup, find_packages

setup(
    name='ocds_sphinx_directives',
    version='0.0.0',
    author='Ben Webb',
    author_email='bjwebb67@googlemail.com',
    url='https://github.com/open-contracting/ocds_sphinx_directives',
    platforms=['any'],
    license='Apache',
    packages=find_packages(),
    entry_points='''
[babel.extractors]
codelists_text = ocds_sphinx_directives:codelists_extract
jsonschema_text = ocds_sphinx_directives:jsonschema_extract
''',
    install_requires=[
        'docutils',
        'requests',
    ],
)
