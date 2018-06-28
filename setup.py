from setuptools import setup

setup(
    name='sphinxcontrib-opencontracting',
    version='0.0.0',
    packages=['sphinxcontrib'],
    install_requires=[
        'docutils',
        'ocdsextensionregistry>=0.0.4',
        'requests',
        'requests-cache',
    ],
    namespace_packages=['sphinxcontrib'],
)
