import sys
import click

from ckanext.validation.model import create_tables, tables_exist


def get_commands():
    return [validation]


@click.group()
def validation():
    """Validation management commands.
    """
    pass


@validation.command()
def init_db():
    """Reinitalize database tables."""
    if tables_exist():
        click.echo("Validation tables already exist")
        sys.exit(0)

    create_tables()

    click.echo("Validation tables created")
