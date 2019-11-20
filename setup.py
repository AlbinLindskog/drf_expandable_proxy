from distutils.core import setup

setup(
    name='Django restframework expandable proxy',
    version='0.0.1',
    description='Expandable objects in Django restframework.',
    long_description=open('README.rst').read(),
    install_requires=[],
    packages=['drf_expandable_proxy'],
    author='Albin Lindskog',
    author_email='albin@zerebra.com',
    url='https://github.com/albinlindskog/drf_expandable_proxy',
    zip_safe=True,
)
