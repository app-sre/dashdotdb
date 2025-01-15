from setuptools import setup


setup(name='dashdotdb',
      packages=['dashdotdb'],
      version=open('VERSION').read().strip(),
      author='Red Hat Application SRE Team',
      author_email="sd-app-sre@redhat.com",
      description='',
      python_requires='>=3.9',
      license="GPLv2+",
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'Framework :: Flask',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: '
            'GNU General Public License v2 or later (GPLv2+)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.9',
      ],
      install_requires=[
            'connexion[swagger-ui] ~= 3.2',
            'Flask ~= 3.1',
            'flask-healthz ~= 1.0.1',
            'Flask-Migrate ~= 4.1',
            'Flask-SQLAlchemy ~= 3.1',
            'SQLAlchemy ~= 2.0.37',
            'psycopg2-binary ~= 2.9',
            'prometheus-client ~= 0.14',
            'gunicorn ~=23.0',
            'openapi-schema-validator ~=0.6.2',
            'jsonschema ~=4.23',
            'markupsafe == 3.0.2'
      ],
      )
