from setuptools import setup, find_packages
import os


setup(
    name='tgt_grease',
    version='2.2.4',
    license="MIT",
    description='GRE Application Service Engine',
    long_description="""
    GREASE is an automation tool for SRE like teams. Rather than providing every solution under the sun, GREASE
    offers developers a framework to develop automation for their needs. GREASE offers a suite of tools and services
    to make automation easy.
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
        'psycopg2',
        'requests',
        'pymongo',
        'psutil',
        'elasticsearch',
        'kafka'
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
