from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='robotouille',
    version='1.0',
    author='Gonzalo Gonzalez',
    author_email='gg387@cornell.edu',
    description='A customizable cooking environment for stress testing LLM agents!',
    packages=find_packages(),
    install_requires=requirements,
)