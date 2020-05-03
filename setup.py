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
          'hug_middleware_cors',
          'SQLAlchemy',
          'SQLAlchemy-serializer',
          'alembic'
      ],
#      packages=[],

      zip_safe=False)