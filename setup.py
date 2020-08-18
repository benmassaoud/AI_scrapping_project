from setuptools import setup

setup(name='ZakariaBenmassaoud_TP',
      version='0.1',
      description='Zakaria Benmassaoud TP',
      author='Zakaria Benmassaoud',
      author_email='benmassaoud@gmail.com',
      packages=['ZakariaBenmassaoud_TP'],
      install_requires=[
          'requests', 'requests_html', 'pyppeteer', 'pyppdf', 'pandas', 'nest_asyncio'
      ],
      zip_safe=False)