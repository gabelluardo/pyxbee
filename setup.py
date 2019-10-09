import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyxbee',
    version='1.0.0.dev1',
    author='Gabriele Belluardo',
    author_email='gabriele.belluardo@outlook.it',
    description='Communication module for Marta (Policumbent)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gabelluardo/pyxbee',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: LGPL License',
        'Operating System :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=['digi-xbee'],
    extras_require={'dev': ['pytest>=5', 'pylint', 'autopep8']},
)
