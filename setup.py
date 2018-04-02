from setuptools import setup

setup(
    name='zxcvbn-python',
    version='4.4.20',
    packages=['zxcvbn'],
    url='https://github.com/dwolfhub/zxcvbn-python',
    download_url='https://github.com/dwolfhub/zxcvbn-python/tarball/v4.4.20',
    license='MIT',
    author='Daniel Wolf',
    author_email='danielrwolf5@gmail.com',
    description='Python implementation of Dropbox\'s realistic password '
                'strength estimator, zxcvbn',
    keywords=['zxcvbn', 'password', 'security'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
