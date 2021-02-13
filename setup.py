from setuptools import setup

setup(
    name='sphinxcontrib-opencontracting',
    version='0.0.0',
    packages=['sphinxcontrib'],
    install_requires=[
        'commonmark',
        'docutils',
        'jsonpointer',
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
