# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
# To use a consistent encoding
from codecs import open
from os import path
import versioneer
from glob import glob

import os
import sys
import subprocess
import shutil

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

class install(_install):
    def run(self):
        self.compile_treetagger()
        self.compile_segphrase()
        _install.run(self)

    def compile_treetagger(self):
        if sys.platform.startswith('darwin'):
            shutil.copy2('autophrase/tools/treetagger/bin/tree-tagger-mac', 'autophrase/tools/treetagger/bin/tree-tagger')
        if sys.platform.startswith('linux'):
            shutil.copy2('autophrase/tools/treetagger/bin/tree-tagger-linux', 'autophrase/tools/treetagger/bin/tree-tagger')
        return

    def compile_segphrase(self):
        CXX = "g++"
        if sys.platform == 'darwin':
            CXX = "g++-6"
        if sys.platform == 'linux':
            CXX = "g++"
        return_code = subprocess.call(["make", "all","CXX="+CXX], cwd="autophrase")
        if return_code > 0:
            exit(return_code)

data_file = [('autophrase/bin', ['autophrase/bin/segphrase_train', 'autophrase/bin/segphrase_segment']),
            ('autophrase/tools/treetagger/bin', ['autophrase/tools/treetagger/bin/tree-tagger'])]

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

cmdclass=versioneer.get_cmdclass()
cmdclass.update({'install': install})

setup(
    name='autophrase',  # Required
    version=versioneer.get_version(),  # Required
    cmdclass=cmdclass,
    description='Automated Phrase Mining from Massive Text Corpora',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/shangjingbo1226/AutoPhrase',  # Optional
    author='',  # Optional
    author_email='',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='phrase mining',  # Optional
    packages=find_packages(),  # Required
    install_requires=[],  # Optional
    include_package_data=True,
    # package_data={
    #     'autophrase': ['bin/segphrase_train', 'bin/segphrase_segment', 'tools/treetagger/bin/tree-tagger']
    # },
    data_files=data_file,  # Optional Wow this is not necessary here!
    entry_points={},
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/shangjingbo1226/AutoPhrase/issues'
    },
)