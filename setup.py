from setuptools import setup, find_packages
import os


setup(
    name='tgt_grease',
    version='2.3.10',
    license="MIT",
    description='Modern distributed automation engine built with love by Target',
    long_description="""
    GREASE is a general purpose distributed automation engine designed to scale to enterprise workloads. We utilize
    MongoDB and a plugin architecture to enable broad automation possibilities via one common core of primitives and
    services.
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: System',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX'
    ],
    keywords='python automated recovery',
    author='James E. Bell Jr.',
    author_email="james.e.bell@target.com",
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3', 'mock'],
    install_requires=[
        'psycopg2-binary',
        'requests',
        'pymongo',
        'psutil',
        'elasticsearch',
        'kafka-python'
    ] + (
         ["pywin32"] if "nt" == os.name else []
        ),
    include_package_data=True,
    zip_safe=False,
    scripts=[
        'bin/grease',
        'bin/grease.ps1'
    ]
)
