from setuptools import setup, find_packages

setup(
    name='lmsh',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyGithub',  # Добавьте другие зависимости здесь
    ],
    entry_points={
        'console_scripts': [
            'lmsh=lmsh.lmsh:main',
        ],
    },
    author='svyatoslav suglobov',
    author_email='svyatoslav.suglobov@gmail.com',
    description='LMS Helper (lmsh) CLI tool',
    url='https://github.com/nup-csai/lms-github',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)