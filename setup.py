from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='gatekeeper',
      version=version,
      description="",
      long_description=""" """,
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "barrel",
          "PyCrypto",
          "cromlech.browser",
          "cromlech.dawnlight",
          "cromlech.security",
          "cromlech.webob",
          "dolmen.forms.crud",
          "dolmen.message",
          "dolmen.sqlcontainer",
          "dolmen.template",
          "dolmen.view",
          "js.bootstrap",
          "setuptools",
          "uvclight[sql]",
          "uvclight[auth]",
          "wsgistate",
          "ul.auth",
          "gk.login",
          "gk.layout",
          "gk.admin",
          "gk.backends",
          "gk.crypto",
      ],
      entry_points={
         'paste.app_factory': [
             'keeper = gatekeeper.app:keeper',
             'timeout = gk.login:timeout',
             'login = gk.login:login',
             'admin = gk.admin:admin',
             'unauthorized = gk.login:unauthorized',
         ],
         'paste.filter_factory': [
             'global_config = gatekeeper.utils:configuration',
         ],
      }
      )
