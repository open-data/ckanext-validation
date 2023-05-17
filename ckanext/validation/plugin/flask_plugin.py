#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ckan.plugins as plugins
from ckanext.validation.blueprints import validation_blueprint
from ckanext.validation.cli import get_commands


class MixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    def get_commands(self):
        return get_commands()

    
    def get_blueprint(self):
        return [validation_blueprint]
