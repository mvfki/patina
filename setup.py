from setuptools import setup, find_packages

setup(
    name="patina",
    version="1.0",
    author="Yichen Wang",
    description="A simulator of the fact that old Android OS make the images greener due to a bug in old Google's Skia library. ",
    packages=find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
    ],
    package_data={
        'patina': [
            'static/styles/*',
            'templates/*'
        ]
    },
    include_package_data=True,
    install_requires=['Flask==1.1.2',
                      'Flask_Session==0.4.0',
                      'opencv-python>=4.5.0'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'patina = patina.__main__:start_web_app'
        ]
    }
)