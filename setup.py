# -*- coding: utf-8 -*-

import json
from distutils.core import setup
from pathlib import Path

import setuptools

from mimesis import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
)

here = Path(__file__).resolve().parent


def get_readme():
    return Path('README.rst').read_text()


class Minimizer(setuptools.Command):
    """Minify content of all json files for all locales."""

    description = 'Minify content of all json files.'
    user_options = []

    def initialize_options(self):
        """Find all files of all locales."""
        self.separators = (',', ':')
        self.data_dir = here / 'mimesis' / 'data'
        self.before_total = 0
        self.after_total = 0
        self.paths = [file.relative_to(self.data_dir) for file in self.data_dir.rglob('*.json')]

    def finalize_options(self):
        pass

    @staticmethod
    def size_of(num):
        for unit in ['B', 'KB', 'MB']:
            if abs(num) < 1024.0:
                return '%3.1f%s' % (num, unit)
            num = num / 1024.0
        return '%.1f' % num

    def minify(self, file_path):
        size_before = file_path.stat().st_size
        self.before_total += size_before
        size_before = self.size_of(size_before)

        json_text = json.loads(file_path.read_text(buffering=1))
        minimized = json.dumps(json_text, separators=self.separators, ensure_ascii=False)

        if file_path.parts:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open('w+', 1) as f:
                f.write(minimized)

        size_after = file_path.stat().st_size
        self.after_total += size_after
        size_after = self.size_of(size_after)

        json_file = file_path.relative_to(file_path.parents[1])

        template = '\033[34m{}\033[0m : ' \
                   '\033[92mminimized\033[0m : ' \
                   '\033[33m{}\033[0m -> \033[92m{}\033[0m'

        print(template.format(json_file,
                              size_before, size_after))

    def run(self):
        """Start json minimizer and exit when all json files were minimized."""
        for rel_path in sorted(self.paths):
            file_path = self.data_dir / rel_path
            self.minify(file_path)

        after = self.size_of(self.after_total)
        before = self.size_of(self.before_total)
        saved = self.size_of(self.before_total - self.after_total)

        template = '\nTotal: ' \
                   '\033[92m{}\033[0m -> \033[92m{}\033[0m. ' \
                   'Compressed: \033[92m{}\033[0m\n'

        print(template.format(before, after, saved))


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=get_readme(),
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    packages=[
        'mimesis',
        'mimesis.data',
        'mimesis.data.int',
        'mimesis.builtins',
        'mimesis.providers',
    ],
    keywords=[
        'fake',
        'mock',
        'data',
        'populate',
        'database',
        'testing',
        'generate',
        'mimesis',
        'dummy',
    ],
    package_data={
        'mimesis': [
            'data/*/*',
            'py.typed',
        ],
    },
    exclude_package_data={
        'mimesis': [
            # It's for development.
            'data/locale_template/*',
        ],
    },
    data_files=[
        ('', ['LICENSE']),
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    cmdclass={
        'minify': Minimizer,
    },
)
