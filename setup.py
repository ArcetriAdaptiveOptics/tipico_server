#!/usr/bin/env python
from setuptools import setup


__version__ = "$Id: setup.py 36 2018-01-28 14:32:11Z lbusoni $"



setup(name='tipico-server',
      description='useless controller of a simulated device with PLICO',
      version='0.9',
      classifiers=['Development Status :: 4 - Beta',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   ],
      long_description=open('README.md').read(),
      url='',
      author_email='lbusoni@gmail.com',
      author='Lorenzo Busoni',
      license='',
      keywords='plico, laboratory, instrumentation control',
      packages=['tipico_server',
                'tipico_server.instrument_controller',
                'tipico_server.process_monitor',
                'tipico_server.scripts',
                'tipico_server.utils',
                ],
      entry_points={
          'console_scripts': [
              'tipico_server_1=tipico_server.scripts.tipico_instrument_controller_1:main',
              'tipico_server_2=tipico_server.scripts.tipico_instrument_controller_2:main',
              'tipico_kill_all=tipico_server.scripts.tipico_kill_processes:main',
              'tipico_start=tipico_server.scripts.tipico_process_monitor:main',
              'tipico_stop=tipico_server.scripts.tipico_stop:main',
          ],
      },
      package_data={
          'tipico_server': ['conf/tipico_server.conf', 'calib/*'],
      },
      install_requires=["plico>=0.14",
                        "tipico>=0.10",
                        "numpy",
                        "ipython",
                        "matplotlib",
                        "scipy",
                        "psutil",
                        "configparser",
                        "six",
                        "appdirs",
                        "pyfits",
                        "futures",
                        ],
      include_package_data=True,
      test_suite='test',
      )
