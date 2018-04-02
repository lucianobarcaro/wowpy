from distutils.core import setup

metadata = {
    'name': 'wowpy',
    'version': '0.0.1',
    'description': 'wowpy is a client library for the World of Warcraft Community API.',
    'long_description': '',
    'author': 'Luciano Barcaro',
    'author_email': 'luciano.barcaro@gmail.com',
    'url': 'https://github.com/lucianobarcaro/wowpy',
    'install_requires': [
        'requests>=2.10'
    ],
    'extras_require': {},
    'license': 'MIT',
    'keywords': ['warcraft', 'api', 'wow', 'auctionhouse', 'community'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
    'packages': [
        'wowpy'
    ]
}

setup(**metadata)
