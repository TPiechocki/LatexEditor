from setuptools import setup

setup(name='latex-editor',
      version='1.0',
      description='Simple Latex text editor',
      author='Tomasz Piechocki',
      author_email='t.piechocki@yahoo.com',
      license='GPL',
      packages=['editor'],
      entry_points = {
            'console_scripts': ['latex-editor=editor.main:main'],
      },
      zip_safe=False)