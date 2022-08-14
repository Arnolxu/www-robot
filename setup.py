from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='www-robot',
    packages=['www-robot'],
    version='1.0.0',
    license='MIT',
    author='Cinar Yilmaz',
    author_email='cinaryilmaz.gnu@gmail.com',
    url='https://github.com/Camroku/www-robot',
    description='A WWW Robot library for Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=['beautifulsoup4'],
    keywords=['www', 'robot', 'python', 'scraping'],
    classifiers=["Operating System :: OS Independent"],
)