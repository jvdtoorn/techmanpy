import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
   long_description = fh.read()

setuptools.setup(
   name='techmanpy-jvdt', # Replace with your own username
   version='1.0',
   description='Python driver for Techman robots',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Jules van der Toorn',
   author_email='julesvandertoorn@gmail.com',
   classifiers=[
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.7',
      'License :: OSI Approved :: MIT License',
      'Operating System :: POSIX :: Linux',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'Natural Language :: English'
   ],
   keywords='techman driver manipulator robotics',
   project_urls={
      'Source': 'https://github.com/jvdtoorn/techmanpy'
   },
   packages=setuptools.find_packages(),
   python_requires='~=3.7',
)