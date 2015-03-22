from subdaap import utils

from flask import render_template, redirect, url_for

import logging
import jinja2
import os

# Logger instance
logger = logging.getLogger(__name__)


def extend_server_app(application, app):
    """
    Since the DAAP server is basically a normal HTTP server, extend it with a
    web interface for easy access and statistics.

    If the DAAPServer was configured with a password, the default username is
    empty and the password is equal to the configured password.

    :param Application application: SubDaap application for information.
    :param Flask app: Flask/DAAPServer to extend.
    """

    # Set the jinja2 loader
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader, jinja2.FileSystemLoader(template_path)])

    app.jinja_env.filters["human_bytes"] = utils.human_bytes

    @app.route("/")
    @app.authenticate
    def index():
        """
        Default index.
        """

        return render_template(
            "index.html", application=application,
            provider=application.provider)

    @app.route("/actions/<action>")
    @app.authenticate
    def actions(action):
        """
        Handle actions and return to index page.
        """

        action = action.lower()
        logger.info("Webserver action: %s", action)

        if action == "shutdown":
            application.stop()
        elif action == "synchronize":
            if not application.provider.lock.locked():
                application.provider.synchronize()
                application.provider.cache()
            else:
                logger.warn("Provider is still locked. Already synchronizing?")

        # Return back to index
        return redirect(url_for("index"))
