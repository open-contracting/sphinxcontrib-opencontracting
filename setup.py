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
    install_requires=[
        'docutils',
        'requests',
    ]
)
