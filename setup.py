from setuptools import setup

setup(
    name='sphinxcontrib-opencontracting',
    version='0.0.1',
    packages=['sphinxcontrib'],
    install_requires=[
        'commonmark',
        'docutils',
        'jsonpointer',
        'MyST-Parser',
        'requests',
        'ocdsextensionregistry>=0.0.8',
    ],
    extras_require={
        'test': [
            'coveralls',
            'lxml',
            'pytest',
            'pytest-cov',
            'Sphinx',
        ],
    },
    namespace_packages=['sphinxcontrib'],
)
