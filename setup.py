from setuptools import setup

description = "A package that enables longstanding asyncio workers to be easily built."
version = '0.1'

requirements = ['asyncio']

tests_require = ['pytest', 'pytest-asyncio']

setup(name='asyncio_worker',
      version=version,
      description=description,
      url='http://github.com/amustafa/asyncio_worker',
      author='Adam Mustafa',
      author_email='amustafa@alum.mit.edu',
      license='MIT',
      packages=['asyncio_worker'],
      install_requires=requirements,
      tests_require=tests_require,
      zip_safe=False)
