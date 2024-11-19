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
            'connexion[swagger-ui] ~= 2.14',
            'Flask ~= 1.1',
            'flask-healthz ~= 0.0.3',
            'Flask-Migrate ~= 2.7',
            'Flask-SQLAlchemy ~= 2.5',
            'SQLAlchemy ~= 1.4.48',
            'psycopg2-binary ~= 2.9',
            'prometheus-client ~= 0.14',
            'gunicorn ~= 20.1',
            'openapi-schema-validator ~= 0.1.5',
            'jsonschema ~=4.23',
            # Newer versions are not compatible with our Flask version
            'markupsafe == 2.0.1'
      ],
      )
