from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='lando.video',
      version=version,
      description="Plugin for redturtle.video",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='RedTurtle Developers',
      author_email='svilplone@redturtle.it',
      url='http://www.redturtle.it',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['lando'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'redturtle.video'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
