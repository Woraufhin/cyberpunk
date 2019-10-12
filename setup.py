from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='cyberpunk',
    version='0.01',
    install_requires=requirements,
    packages=[''],
    url='https://github.com/Woraufhin/cyberpunk',
    license='MIT',
    author='Juan Schandin',
    author_email='juan.schandin@filo.uba.ar',
    description='AI Chess Wars'
)
