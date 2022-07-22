from setuptools import setup

setup(
    name='sttutter-sound-bytter',
    version='0.0.1',
    packages=['loader', 'logger', 'slicer', 'tagger', 'tester', 'audioprocessor'],
    package_dir={'': 'app'},
    url='www.sttutter.com',
    license='MIT',
    author='Sttutter',
    author_email='sound.bytter@sttutter.com',
    description='Automaticall create audio clips'
)
