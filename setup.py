from os.path import dirname, join
from setuptools import find_packages, setup

package_name = "crest"

def read(path):
    with open(join(dirname(__file__), path)) as f:
        return f.read()

setup(name=package_name,
      version='0.0.1',
      description='CLI to access RESTful service',
      long_description=read("README.rst"),
      url="https://github.com/manishtomar/crest",

      author='Manish Tomar',
      author_email='manish.tomar@gmail.com',
      maintainer='Manish Tomar',
      maintainer_email='manish.tomar@gmail.com',

      entry_points={'console_scripts': ['crest = crest.cli:main']},

      license='MIT',
      keywords="restful cli",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python :: 2 :: Only",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP"
      ],

      packages=find_packages(),
      install_requires=['requests']
      )
