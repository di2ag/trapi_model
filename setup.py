"""Setup file for Translator Reasoner API (TRAPI) Model package."""
from setuptools import setup

with open('README.md', 'r') as stream:
    long_description = stream.read()

setup(
    name='trapi_model',
    version='0.0.0',
    author='Chase Yakaboski',
    author_email='chase.th@dartmouth.edu',
    url='https://github.com/di2ag/trapi_model',
    description='Python Data Classes for TRAPI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=[
        'trapi_model',
        'trapi_model.data',
        'trapi_model.data.biolink_schemas',
        'trapi_model.data.trapi_schemas',
        'trapi_model.biolink',
        'trapi_model.biolink.constants',
        'trapi_model.schemas'
        ],
    package_data={
        'trapi_model.data.biolink_schemas': ['*.yaml', '*.yml'],
        'trapi_model.data.trapi_schemas': ['*.yaml', '*.yml'],
        'trapi_model.biolink.constants': ['*.csv'],
        'trapi_model.schemas':['*.json'],
        },
    include_package_data=True,
    install_requires=[
        'jsonschema',
        'bmt==0.10.0',
        'deepdiff',
        'reasoner_validator==3.3.1'
    ],
    zip_safe=False,
    python_requires='>=3.6',
)
