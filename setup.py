from setuptools import setup

setup(
  name='Vio',
  version='0.0.9',
  description='A Wrapper for the Vio API',
  url='https://viopy.readthedocs.io/',
  author="Meaning",
  license="MIT",
  packages=['vio'],
  install_requires=[
    "websockets==10.3",
    "httpx==0.22.0",
    "terminaltables==3.1.10"
  ],
  classifiers=[
    'Development Status :: 1 - Planning',
    'Intended Audience :: WEBSITE USERS',
    'License :: OSI Approved :: MIT License',  
    'Operating System :: WINDOWS',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Typing :: Typed'
  ]
)