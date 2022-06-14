from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name='Vio',
  version='0.0.12',
  description='A Wrapper for the Vio API',
  url='https://viopy.readthedocs.io/',
  author="Meaning",
  long_description=long_description,
  long_description_content_type="text/markdown",
  license="MIT",
  packages=['vio'],
  install_requires=[
    "websockets==10.3",
    "httpx==0.22.0",
    "terminaltables==3.1.10"
  ],
  classifiers=[
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Typing :: Typed'
  ]
)