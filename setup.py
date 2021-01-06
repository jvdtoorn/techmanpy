import setuptools
import sys

if sys.version_info[:2] < (3, 8): raise Exception("'techmanpy' requires Python >= 3.8")

with open('README.md', 'r', encoding='utf-8') as fh:
   long_description = fh.read()

setuptools.setup(
   name='techmanpy',
   version='1.1',
   description='Communication driver for Techman robots',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Jules van der Toorn',
   author_email='julesvandertoorn@gmail.com',
   license='MIT',
   classifiers=[
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.8',
      'License :: OSI Approved :: MIT License',
      'Operating System :: POSIX :: Linux',
      'Intended Audience :: Science/Research',
      'Natural Language :: English'
   ],
   keywords='techman driver manipulator robotics',
   url='https://github.com/jvdtoorn/techmanpy',
   project_urls={
      'Source': 'https://github.com/jvdtoorn/techmanpy'
   },
   packages=setuptools.find_packages(),
   package_dir={'': '.'},
   python_requires='~=3.8',
)