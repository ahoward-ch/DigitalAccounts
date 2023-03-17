from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='digiaccounts',
    version='0.1',
    author='Alex Howard',
    author_email='ahoward@companieshouse.gov.uk',
    maintainer='Alex Howard',
    maintainer_email='ahoward@companieshouse.gov.uk',
    description='An automated tool for extracting key facts from Companies House (UK) digital accounts files',
    long_description=long_description,
    packages=['digiaccounts'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'oracledb',
        'py_xbrl',
        'pymongo==4.3.3',
        'pytest==7.1.2',
        'python_dateutil==2.8.2',
    ],
)
