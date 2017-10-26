from setuptools import setup, find_packages
import os


setup(
    name='tgt_grease',
    version='1.5.5',
    description='GRE Application Service Engine',
    long_description="Automation Engine for operations",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: System',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='python automated recovery incident',
    author='james.e.bell@target.com',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    install_requires=[
        'psycopg2',
        'requests',
        'pymongo',
        'sqlalchemy',
        'python-dotenv',
        'psutil'
    ] + (
         ["pypiwin32"] if "nt" == os.name else []
        ),
    include_package_data=True,
    zip_safe=False,
    scripts=[
        'bin/grease',
        'bin/grease-daemon',
        'bin/greasectl.py',
        'bin/greasectl.ps1'
    ]
)
