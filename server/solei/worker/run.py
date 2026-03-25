from solei import tasks
from solei.logfire import configure_logfire
from solei.logging import configure as configure_logging
from solei.posthog import configure_posthog
from solei.sentry import configure_sentry
from solei.worker import broker

configure_sentry()
configure_logfire("worker")
configure_logging(logfire=True)
configure_posthog()

__all__ = ["broker", "tasks"]
