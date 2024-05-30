from setuptools import setup

setup(
    name='connect4-3d',
    options={
        'build_apps': {
            # Build connect4-3d as a console application
            'console_apps': {
                'connect4-3d': 'main.py',
            },

            'icons': {
                'connect4-3d': ["icons/icon-256.png", "icons/icon-128.png", "icons/icon-48.png", "icons/icon-32.png", "icons/icon-16.png"]
            },


            # Specify which files are included with the distribution
            'include_patterns': [
                'images/*.png',
                'models/*.jpg',
                'models/*.bam',

            ],

            'exclude_patterns': [
                'repartition.txt'
            ],

            'platforms': ['win_amd64'], # remove this if you want to build for other platforms
                                        # see at https://docs.panda3d.org/1.10/python/distribution/building-binaries

            # Include the OpenGL renderer
            'plugins': [
                'pandagl',
            ],
        }
    }
)
