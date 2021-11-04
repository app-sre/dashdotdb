from setuptools import setup


setup(name='dashdotdb',
      packages=['dashdotdb'],
      version=open('VERSION').read().strip(),
      author='Red Hat Application SRE Team',
      author_email="sd-app-sre@redhat.com",
      description='',
      python_requires='>=3.6',
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
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
      ],
      install_requires=[
            'connexion[swagger-ui] ~= 2.7',
            'Flask ~= 1.1',
            'flask-healthz ~= 0.0.3',
            'Flask-Migrate ~= 2.5',
            'Flask-SQLAlchemy ~= 2.4',
            'psycopg2-binary ~= 2.8',
            'prometheus-client ~= 0.8',
            'gunicorn ~= 20.0'
      ],
      )
