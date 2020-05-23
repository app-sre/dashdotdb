from setuptools import setup, find_packages


setup(name='dashdotdb',
      packages=['dashdotdb'],
      version=open('VERSION').read().strip(),
      author='Red Hat Application SRE Team',
      author_email="sd-app-sre@redhat.com",
      description='',
      python_requires='>=3.6',
      license="GPLv2+",
      package_data={'': ['schemas/swagger.yaml']},
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'Framework :: Flask',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: '
            'GNU General Public License v2 or later (GPLv2+)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
      ],
      install_requires=[
            'sqlalchemy ~= 1.3',
            'tabulate ~= 0.8',
            'psycopg2-binary ~= 2.8',
      ],
      entry_points=
      {
            'console_scripts': [
                  'dashdotdb = dashdotdb.cli.dashdotdb:main',
                  'dashdotdb-admin = dashdotdb.cli.dashdotdb_admin:main',
            ],
            'plugins': [
                  'imagemanifestvuln = dashdotdb.cli.plugins.imagemanifestvuln:ImageManifestVuln',
                  'dummy = dashdotdb.cli.plugins.dummy:Dummy',
            ]
      }
      )
