from setuptools import setup

setup(
    name='sphinxcontrib-opencontracting',
    version='0.0.0',
    author='Ben Webb',
    author_email='bjwebb67@googlemail.com',
    packages=['sphinxcontrib'],
    url='https://github.com/open-contracting/sphinxcontrib-opencontracting',
    install_requires=[
        'docutils',
        'requests',
    ],
    namespace_packages=['sphinxcontrib'],
)
