from setuptools import setup, find_packages
import sys, os

version = '0.8.4'

f = open('README.txt')
readme = "".join(f.readlines())
f.close()

setup(name='opencore',
      version=version,
      description="openplans.org software",
      long_description=readme,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='openplans openplans.org topp',
      author='The Open Planning Project',
      author_email='info@openplans.org',
      url='http://topp.openplans.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=['https://svn.openplans.org/svn/topp.deploy/trunk/dependency_links_local.html',
                        'https://svn.openplans.org/svn/OpencoreRedirect/trunk#egg=OpencoreRedirect'],
      install_requires=[
          # -*- Extra requirements: -*-
          'topp.featurelets',
          'memojito',
          'OpencoreRedirect',
          'httplib2',
          'simplejson'
      ]
      )

