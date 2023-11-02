"""
Flask-DotEnv

:copyright: (c) 2015-2019 Yasuhiro Asaka.
:license: BSD 2-Clause License
"""

from __future__ import absolute_import
import ast
import os
import re
import warnings

def string_or_numeric(value):
    try:
        int_value = int(value)
        return int_value
    except:
        try: 
            float_value = float(value)
            return float_value
        except:
            return value


class DotEnv(object):
    """The .env file support for Flask."""

    def __init__(self, app=None):
        self.app = app
        self.verbose_mode = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app, env_file=None, verbose_mode=False):
        """Imports .env file."""
        if self.app is None:
            self.app = app
        self.verbose_mode = verbose_mode

        if env_file is None:
            env_file = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(env_file):
            warnings.warn("can't read {0} - it doesn't exist".format(env_file))
        else:
            self.__import_vars(env_file)

    def __import_vars(self, env_file):
        """Actual importing function."""
        with open(env_file, "r") as f:  # pylint: disable=invalid-name
            for line in f:

                try:
                    line = line.lstrip()
                    if line.startswith('export'):
                        line = line.replace('export', '', 1)
                    if line.startswith("#"):
                        continue
                    key, val = line.strip().split('=', 1)
                    key = key.strip()
                    if "#" in val:
                        val = val.split('#')[0].strip() # handle trailing comments
                except ValueError:  # Take care of blank or comment lines
                    pass
                else:
                    if not callable(val):
                        if self.verbose_mode:
                            if key in self.app.config:
                                print(
                                    " * Overwriting an existing config var:"
                                    " {0} => {1}".format(key, val))
                            else:
                                print(
                                    " * Setting an entirely new config var:"
                                    " {0} => {1}".format(key, val))
                        string_val = re.sub(
                            r"\A[\"']|[\"']\Z", "", val)
                        self.app.config[key] = string_or_numeric(string_val)

    def eval(self, keys):
        """
        Examples:
            Specify type literal for key.

            >>> env.eval({MAIL_PORT: int})
        """
        for k, v in keys.items():  # pylint: disable=invalid-name
            if k in self.app.config:
                try:
                    val = ast.literal_eval(self.app.config[k])
                    if isinstance(val, v):
                        if self.verbose_mode:
                            print(
                                " * Casting a denoted var as a literal:"
                                " {0} => {1}".format(k, v)
                            )
                        self.app.config[k] = val
                    else:
                        print(
                            " ! Does not match with specified type:"
                            " {0} => {1}".format(k, v))
                except (ValueError, SyntaxError):
                    print(" ! Could not evaluate as literal type:"
                          " {0} => {1}".format(k, v))

    def alias(self, maps):
        """
        Examples:
            Make alias var -> as.

            >>> env.alias(maps={
              'TEST_DATABASE_URL': 'SQLALCHEMY_DATABASE_URI',
              'TEST_HOST': 'HOST'
            })
        """
        for k, v in maps.items():  # pylint: disable=invalid-name
            if self.verbose_mode:
                print(
                    " * Making a specified var as an alias:"
                    " {0} -> {1}".format(v, k))
            self.app.config[v] = self.app.config[k]
