from setuptools import setup

setup(name='mastok',
      version='0.1',
      description='Mastok server',
      url='https://github.com/biwano/mastok.git',
      author='Bruno Ilponse',
      author_email='bruno.ilponse@gmail.com',
      license='MIT',
      install_requires=[
          'hug',
          'SQLAlchemy',
          'SQLAlchemy-serializer',
          'alembic',
          'marshmallow',
          'requests'
      ],
      extras_require={
          'dev': [
              'pylint'
          ]
      },
      #      packages=[],

      zip_safe=False)
