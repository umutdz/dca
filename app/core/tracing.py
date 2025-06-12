"""
TODO: must be added tracing to the project
NOTE: could be jager or opentelemetry depends on the project
import logging

from elasticapm import get_client
from elasticapm.contrib.starlette import make_apm_client

from app.core.config import config

logger = logging.getLogger(__name__)


def apm_client():
    if config.APP_ENV == "LOCAL":
        return

    client = get_client()
    if client:
        return client
    else:
        apm_config = {
            "SERVICE_NAME": config.APP_APM_NAME,
            "SECRET_TOKEN": "",
            "SERVER_URL": config.ELASTIC_APM_SERVER_URL,
            "ENVIRONMENT": config.APP_ENV,
            "DEBUG": config.APP_DEBUG,
            "ENABLED": False if config.APP_ENV == "LOCAL" else True,
            "TRANSACTION_SAMPLE_RATE": 1.0,
            "COLLECT_LOCAL_VARIABLES": "all",
            "SPAN_FRAMES_MIN_DURATION": 0,
            "LOCAL_VAR_LIST_MAX_LENGTH": 9999,
            "LOCAL_VAR_DICT_MAX_LENGTH": 9999,
            "LOCAL_VAR_MAX_LENGTH": 9999,
            "FILTER_EXCEPTION_TYPES": ["utils.exceptions.schemas.RequestTimeoutException"],
        }
        return make_apm_client(apm_config)


# Initialize APM clients
app_apm = apm_client()
"""
