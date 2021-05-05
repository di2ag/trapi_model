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
        ],
    package_data={'trapi_model.data': ['*.yaml']},
    include_package_data=True,
    install_requires=[
        'pyyaml>=5.1',
        'jsonschema',
        'bmt',
        'git+git://github.com/di2ag/reasoner-validator@master#egg=reasoner-validator',
    ],
    zip_safe=False,
    python_requires='>=3.6',
)
