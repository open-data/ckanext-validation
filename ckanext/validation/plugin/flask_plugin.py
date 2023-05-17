#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import ckan.plugins as plugins
from ckanext.validation.blueprints import validation_blueprint
from ckanext.validation.model import create_tables, tables_exist

class MixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    def get_commands(self):
        import click

        @click.group("validation")
        def init_db():
            if tables_exist():
                click.echo("Validation tables already exist")
                sys.exit(0)

            create_tables()

            click.echo("Validation tables created")

        return [init_db]

    
    def get_blueprint(self):
        return [validation_blueprint]
