import sys
import click

from ckanext.validation.model import create_tables, tables_exist

# (canada fork only): add run_validation command
from ckan.plugins.toolkit import get_action, ObjectNotFound
from ckanext.validation.jobs import run_validation_job


@click.group()
def validation():
    """Harvests remotely mastered metadata."""
    pass


@validation.command()
def init_db():
    """Creates the necessary tables in the database."""
    if tables_exist():
        print(u"Validation tables already exist")
        sys.exit(0)

    create_tables()
    print(u"Validation tables created")


# (canada fork only): add run_validation command
@validation.command()
@click.option('-r', '--resource-id', type=click.STRING, help='A CKAN Resource ID.', required=True)
def run_validation(resource_id):
    """Runs validation instantly for a given resource."""
    try:
        resource = get_action('resource_show')({"ignore_auth": True}, {"id": resource_id})
    except ObjectNotFound:
        click.echo("Resource not found: %s" % resource_id)
        click.Abort
    run_validation_job(resource)
