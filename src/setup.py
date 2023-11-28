from pip._internal.req import parse_requirements
from setuptools import setup, find_packages
from os.path import join, dirname, abspath

import network_rail

install_reqs = parse_requirements('requirements.txt', session="package")
reqs = [str(ir.requirement) for ir in install_reqs]
reqs_file = abspath(join(dirname(__file__), "requirements.txt"))

with open(reqs_file, "r", encoding="utf-8") as fh:
    setup(
        name='railfeed',
        version=network_rail.__version__,
        author='Sureya Sathiamoorthi',
        author_email='sureya.sathiamoorthi@and.digital',
        description='Extraction framework for PMU',
        url='https://github.com/andSureya/national_rail',
        packages=find_packages(),
        install_requires=reqs,
        python_requires='>=3.10',
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Operating System :: OS Independent",
        ],
        entry_points={
            'console_scripts': [
                'railfeed = network_rail.application:main'
            ],
        }
    )