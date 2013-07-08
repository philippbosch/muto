from setuptools import setup, find_packages

setup(
    name='muto',
    version=__import__('muto').__version__,
    description='Server and corresponding client library for ImageMagick-based image manipulation and conversion',
    author='Philipp Bosch',
    author_email='hello@pb.io',
    url='http://github.com/philippbosch/muto',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=open('requirements.txt').read().split(),
    test_suite='tests',
)
