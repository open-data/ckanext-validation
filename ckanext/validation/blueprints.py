# -*- coding: utf-8 -*-
from flask import Blueprint

from ckanext.validation.controller import validation


validation_blueprint = Blueprint('validation', __name__)


def read(id, resource_id):
    return validation(id, resource_id)


validation_blueprint.add_url_rule("/dataset/<id>/resource/<resource_id>/validation",
                                  view_func=read,
                                  methods=['GET'])