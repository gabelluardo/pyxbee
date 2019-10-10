import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyxbee',
    version='0.1',
    author='Gabriele Belluardo',
    author_email='gabbelo@outlook.it',
    description='Communication module for Marta (Policumbent)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gabelluardo/pyxbee',
    packages=['pyxbee'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=['digi-xbee'],
    extras_require={'dev': ['pytest>=5', 'pylint', 'autopep8']},
)
