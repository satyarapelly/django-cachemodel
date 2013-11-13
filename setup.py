from setuptools import setup, find_packages
import os

execfile(os.path.join(os.path.dirname(__file__), 'cachemodel/version.py'))


setup(
    name='django-cachemodel',
    version=".".join(map(str, VERSION)),
    packages = find_packages(),

    author = 'Concentric Sky',
    author_email = 'django@concentricsky.com',
    description = 'Concentric Sky\'s cachemodel library',
    license = 'Apache2'
)
