from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='protheus',
        version='0.0.3',
        # scripts=['protheus'],
        author='Henrique Luiz',
        author_email='henrique.luiz@totvs.com.br',
        description='A command-line interface for helper managemente your environment Portheus',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/HenriqueLuizz/protheus-cli',
        project_urls={  # Optional
        'Bug Reports': 'https://github.com/HenriqueLuizz/protheus-cli/issues',
        # 'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://saythanks.io/to/henriqueluiz_silva%40yahoo.com.br',
        'Source': 'https://github.com/HenriqueLuizz/protheus-cli',
    },
        # package_dir={'': 'src'},  # Optional
        packages=find_packages(),
        include_package_data=True,
        install_requires=['schedule~=0.6.0', 'click~=7.1.2'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
