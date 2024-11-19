import sys
import click

from ckanext.validation.model import create_tables, tables_exist

# (canada fork only): add run_validation command
from ckan.plugins.toolkit import get_action, ObjectNotFound


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
@click.option('-r', '--resource-id', type=click.STRING, help='A CKAN Resource ID.', required=False)
@click.option('-d', '--dataset-id', type=click.STRING, help='A CKAN Dataset ID.', required=False)
@click.option('-s', '--skip-xloader', type=click.BOOL, help='Skip XLoadering the resource after validation.', is_flag=True, default=False)
@click.option('-S', '--sync', type=click.BOOL, help='Run the validation job in Sync mode (right away in the CLI).', is_flag=True, default=False)
def run_validation(resource_id=None, dataset_id=None, skip_xloader=False, sync=False):
    """Runs validation instantly for a given dataset or resource."""
    if resource_id and dataset_id:
        click.echo("--resource-id and --dataset-id are mutually exclusive")
        click.Abort
    resources = []
    if resource_id:
        try:
            resources.append(get_action('resource_show')({"ignore_auth": True}, {"id": resource_id}))
        except ObjectNotFound:
            click.echo("Resource not found: %s" % resource_id)
            click.Abort
    if dataset_id:
        try:
            dataset = get_action('package_show')({"ignore_auth": True}, {"id": dataset_id})
            for resource in dataset.get('resources'):
                resources.append(resource)
        except ObjectNotFound:
            click.echo("Dataset not found: %s" % resource_id)
            click.Abort
    for resource in resources:
        get_action('resource_validation_run')({"ignore_auth": True}, {"resource_id": resource.get('id'),
                                                                      "async": False if sync else True,
                                                                      "skip_xloader": skip_xloader})
    click.echo("\nDONE!")
