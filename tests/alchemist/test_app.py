# -*- coding: utf-8 -*-
from alchemist.test import settings
from flask import Flask
from os import path
import os
import alchemist


class TestSettings:

    def test_project(self):
        self.app = Flask('tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('A_SETTING', 1)

    def test_missing_project(self):
        """
        Should succeed and not raise if the project does not contain
        a settings file.
        """

        self.app = Flask('alchemist')
        with settings(self.app):
            alchemist.configure(self.app)

    def test_component(self):
        self.app = Flask('tests.a')
        with settings(self.app, COMPONENTS=['tests.a.b']):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

    def test_project_as_component(self):
        """
        Should not merge the project settings in twice even if
        it is listed in the COMPONENTS array.
        """

        self.app = Flask('tests.a')
        with settings(self.app, COMPONENTS=['tests.a.b', 'tests.a']):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

    def test_global_env(self):
        """
        Should override settings from the file specified in the
        ALCHEMIST_SETTINGS_MODULE environ variable.
        """

        filename = path.join(path.dirname(__file__), '../a/b/settings.py')
        os.environ['ALCHEMIST_SETTINGS_MODULE'] = filename

        self.app = Flask('tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

        del os.environ['ALCHEMIST_SETTINGS_MODULE']

    def test_project_env(self):
        """
        Should override settings from the file specified in the
        <project>_SETTINGS_MODULE environ variable.
        """

        filename = path.join(path.dirname(__file__), '../a/b/settings.py')
        os.environ['TESTS_A_SETTINGS_MODULE'] = filename

        self.app = Flask('tests.a')
        with settings(self.app):
            alchemist.configure(self.app)

            assert self.app.config.get('B_SETTING', 1)
            assert self.app.config.get('A_SETTING', 5)

        del os.environ['TESTS_A_SETTINGS_MODULE']


class TestApplication:

    @staticmethod
    def _clear_cache():
        from alchemist import app
        type(app).__dict__['_find_application']._cache.clear()

    def setup(self):
        self._clear_cache()

    def teardown(self):
        self._clear_cache()

    def test_stack(self):
        from tests.a.example import application

        assert application.name == 'tests.a'

    def test_env(self):
        os.environ['ALCHEMIST_APPLICATION'] = 'tests.a'

        from tests.a.b.example import application

        assert application.name == 'tests.a'

        del os.environ['ALCHEMIST_APPLICATION']

    def test_env_direct(self):
        os.environ['ALCHEMIST_APPLICATION'] = 'tests.a.b'

        from alchemist.app import application

        assert application.name == 'tests.a.b'

        del os.environ['ALCHEMIST_APPLICATION']
