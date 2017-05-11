"""Bootstrap HassIO."""
import logging
import os
import signal

from colorlog import ColoredFormatter

from .const import SOCKET_DOCKER
from .config import CoreConfig

_LOGGER = logging.getLogger(__name__)


def initialize_system_data(websession):
    """Setup default config and create folders."""
    config = CoreConfig(websession)

    # homeassistant config folder
    if not config.path_config.is_dir():
        _LOGGER.info(
            "Create Home-Assistant config folder %s", config.path_config)
        config.path_config.mkdir()

    # homeassistant ssl folder
    if not config.path_ssl.is_dir():
        _LOGGER.info("Create Home-Assistant ssl folder %s", config.path_ssl)
        config.path_ssl.mkdir()

    # homeassistant addon data folder
    if not config.path_addons_data.is_dir():
        _LOGGER.info("Create Home-Assistant addon data folder %s",
                     config.path_addons_data)
        config.path_addons_data.mkdir(parents=True)

    if not config.path_addons_local.is_dir():
        _LOGGER.info("Create Home-Assistant addon local repository folder %s",
                     config.path_addons_local)
        config.path_addons_local.mkdir(parents=True)

    if not config.path_addons_git.is_dir():
        _LOGGER.info("Create Home-Assistant addon git repositories folder %s",
                     config.path_addons_git)
        config.path_addons_git.mkdir(parents=True)

    if not config.path_addons_build.is_dir():
        _LOGGER.info("Create Home-Assistant addon build folder %s",
                     config.path_addons_build)
        config.path_addons_build.mkdir(parents=True)

    # homeassistant backup folder
    if not config.path_backup.is_dir():
        _LOGGER.info("Create Home-Assistant backup folder %s",
                     config.path_backup)
        config.path_backup.mkdir()

    return config


def initialize_logging():
    """Setup the logging."""
    logging.basicConfig(level=logging.INFO)
    fmt = ("%(asctime)s %(levelname)s (%(threadName)s) "
           "[%(name)s] %(message)s")
    colorfmt = "%(log_color)s{}%(reset)s".format(fmt)
    datefmt = '%y-%m-%d %H:%M:%S'

    # suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    logging.getLogger().handlers[0].setFormatter(ColoredFormatter(
        colorfmt,
        datefmt=datefmt,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    ))


def check_environment():
    """Check if all environment are exists."""
    for key in ('SUPERVISOR_SHARE', 'SUPERVISOR_NAME',
                'HOMEASSISTANT_REPOSITORY'):
        try:
            os.environ[key]
        except KeyError:
            _LOGGER.fatal("Can't find %s in env!", key)
            return False

    if not SOCKET_DOCKER.is_socket():
        _LOGGER.fatal("Can't find docker socket!")
        return False

    return True


def reg_signal(loop, hassio):
    """Register SIGTERM, SIGKILL to stop system."""
    try:
        loop.add_signal_handler(
            signal.SIGTERM, lambda: loop.create_task(hassio.stop()))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGTERM")

    try:
        loop.add_signal_handler(
            signal.SIGHUP, lambda: loop.create_task(hassio.stop()))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGHUP")

    try:
        loop.add_signal_handler(
            signal.SIGINT, lambda: loop.create_task(hassio.stop()))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGINT")