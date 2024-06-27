# encoding: utf-8

from flask import Blueprint

# (canada fork only): ckantoolkit -> toolkit
# (canada fork only): c -> g
from ckan.plugins.toolkit import g, NotAuthorized, ObjectNotFound, abort, _, render, get_action

validation = Blueprint("validation", __name__)


def read(id, resource_id):

    try:
        validation = get_action(u"resource_validation_show")(
            {u"user": g.user}, {u"resource_id": resource_id}
        )

        resource = get_action(u"resource_show")({u"user": g.user}, {u"id": resource_id})

        dataset = get_action(u"package_show")(
            {u"user": g.user}, {u"id": resource[u"package_id"]}
        )

        # Needed for core resource templates
        g.package = g.pkg_dict = dataset
        g.resource = resource

        return render(
            u"validation/validation_read.html",
            extra_vars={
                u"validation": validation,
                u"resource": resource,
                u"dataset": dataset,
                u"pkg_dict": dataset,
            },
        )

    except NotAuthorized:
        abort(403, _(u"Unauthorized to read this validation report"))
    except ObjectNotFound:

        abort(404, _(u"No validation report exists for this resource"))


validation.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/validation", view_func=read
)
