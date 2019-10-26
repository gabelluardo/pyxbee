import setuptools
import re

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('pyxbee/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

setuptools.setup(
    name='pyxbee',
    version=version,
    author='Gabriele Belluardo',
    author_email='gabriele.belluardo@outlook.it',
    description='Communication module for Marta (Policumbent)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gabelluardo/pyxbee',
    packages=['pyxbee'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=['digi-xbee', 'ordered-set'],
    extras_require={'dev': ['pytest>=5', 'pylint', 'autopep8']},
)
