import os

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="compgen2",
    author="CorrelAid",
    description=("Provides the compgen2 package that allows to match locations against the GOV."),
    long_description=read("README.md"),
    packages=["compgen2"],
    package_dir={"": "src"},
    version="1.0",
    install_requires=[
        "BeautifulSoup4",
        "html5lib",
        "jupytext",
        "lxml",
        "numpy",
        "pandas",
        "pyarrow",
        "pyperclip",
        "pytest",
        "tqdm",
    ],
    entry_points={
        'console_scripts': [
            'compgen2=compgen2.app:main',
        ]
    }
)
