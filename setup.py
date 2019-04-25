import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

basedir = os.path.normpath(
    os.path.abspath(os.path.dirname(__file__))
)

with open(os.path.join(basedir, 'README.md')) as readme:
    README = readme.read()

setup(
    name='djadyen',
    version='1.1.0',
    license='BSD',

    # packaging
    install_requires=[
        'Django>=1.8',
        'django-choices',
        'requests',
    ],
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),

    # tests
    test_suite='runtests.runtests',
    tests_require=['coverage'],

    # metadata
    description='A Django package to intergrade Adyen in your project.',
    long_description=README,
    url='https://github.com/maykinmedia/djadyen',
    author='Maykin Media, Jorik Kraaikamp',
    author_email='jorik.kraaikamp@maykinmedia.nl',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
