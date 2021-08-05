"""Console script for vmwaretool."""
import click
import click_completion
import logging as python_logging
import os
from oslo_config import cfg
from oslo_log import log as logging
import sys

import vmwaretool
from vmwaretool import utils
from vmwaretool import vmware_ops

CONF = cfg.CONF
LOG = logging.getLogger(utils.DOMAIN)
logging.register_options(CONF)


def custom_startswith(string, incomplete):
    """A custom completion match that supports case insensitive matching."""
    if os.environ.get('_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


click_completion.core.startswith = custom_startswith
click_completion.init()


@click.command()
@click.option('--disable-spinner', is_flag=True, default=False,
              help='Disable all terminal spinning wait animations.')
@click.option(
    "-c",
    "--config-file",
    "config_file",
    show_default=True,
    default=utils.DEFAULT_CONFIG_FILE,
    help="The aprsd config file to use for options.",
)
@click.option(
    "--loglevel",
    default="DEBUG",
    show_default=True,
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        case_sensitive=False,
    ),
    show_choices=True,
    help="The log level to use for aprsd.log",
)
@click.version_option()
def main(disable_spinner, config_file, loglevel):
    """Console script for vmwaretool."""
    global LOG, CONF

    click.echo("config_file = {}".format(config_file))
    if config_file != utils.DEFAULT_CONFIG_FILE:
        config_file = sys.argv[1:]
    else:
        config_file = ["--config-file", config_file]

    CONF(config_file, project='vmwaretool', version=vmwaretool.__version__)
    python_logging.captureWarnings(True)
    utils.setup_logging()

    CONF.log_opt_values(LOG, utils.LOG_LEVELS[loglevel])

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
