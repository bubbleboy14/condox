from setuptools import setup

setup(
    name='condox',
    version="0.1",
    author='Mario Balibrera',
    author_email='mario.balibrera@gmail.com',
    license='MIT License',
    description='document conversion tools',
    long_description='convert html to latex and docx',
    packages=[
        'condox'
    ],
    zip_safe = False,
    install_requires = [
        "fyg >= 0.1.4"
    ],
    entry_points = '''''',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
