"""
    **Flask App Configuration Settings**
    *Python Version 3.8 and above*
    Used to setup environment variables for python flask app
"""
__developer__ = "mobius-crypt"
__email__ = "mobiusndou@gmail.com"
__twitter__ = "@blueitserver"
__github_repo__ = "https://github.com/freelancing-solutions/memberships-and-affiliate-api"
__github_profile__ = "https://github.com/freelancing-solutions/"

import os
import typing
# noinspection PyPackageRequirements
from decouple import config
import datetime


class Config:
    """
        **APP Configuration Settings**
            configuration variables for setting up the application
    """
    # TODO - Clean up configuration settings
    def __init__(self) -> None:
        # APP URLS
        self.BASE_URL: str = os.environ.get("BASE_URL") or config("BASE_URL")
        self.ADMIN_APP_BASEURL = os.environ.get("ADMIN_APP_BASEURL") or config("ADMIN_APP_BASEURL")
        self.CLIENT_APP_BASEURL = os.environ.get("CLIENT_APP_BASEURL") or config("CLIENT_APP_BASEURL")
        self.AUTH_URLS: list = [self.BASE_URL, self.ADMIN_APP_BASEURL, self.CLIENT_APP_BASEURL]

        # MAILGUN Keys
        self.MAILGUN_DOMAIN: str = os.environ.get("MAILGUN_DOMAIN") or config("MAILGUN_DOMAIN")
        self.MAILGUN_API_KEY: str = os.environ.get("MAILGUN_API_KEY") or config("MAILGUN_API_KEY")
        self.MAILGUN_NO_RESPONSE: str = os.environ.get("MAILGUN_NO_RESPONSE") or config("MAILGUN_NO_RESPONSE")
        self.MAILGUN_VALIDATION_KEY: str = os.environ.get("MAILGUN_VALIDATION_KEY") or config("MAILGUN_VALIDATION_KEY")
        self.MAILGUN_WEBHOOK_KEY: str = os.environ.get("MAILGUN_WEBHOOK_KEY") or config("MAILGUN_WEBHOOK_KEY")

        self.NO_RESPONSE_EMAIL: str = os.environ.get("NO_RESPONSE_EMAIL") or config("NO_RESPONSE_EMAIL")
        self.SMTP_SERVER_URI: str = os.environ.get("SMTP_SERVER_URI") or config("SMTP_SERVER_URI")
        self.SMTP_SERVER_PASSWORD: str = os.environ.get("SMTP_SERVER_PASSWORD") or config("SMTP_SERVER_PASSWORD")
        self.SMTP_SERVER_USERNAME: str = os.environ.get("SMTP_SERVER_USERNAME") or config("SMTP_SERVER_USERNAME")

        self.PROJECT: str = os.environ.get("PROJECT") or config("PROJECT")
        self.APP_NAME: str = os.environ.get("APP_NAME") or config("APP_NAME")

        self.ORGANIZATION_ID: str = os.environ.get("ORGANIZATION_ID") or config("ORGANIZATION_ID")
        self.ADMIN_UID: str = os.environ.get("ADMIN_UID") or config("ADMIN_UID")
        self.DEFAULT_ACCESS_RIGHTS: typing.List[str] = ["visitor", "user", "super_user", "admin"]
        self.ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL") or config("ADMIN_EMAIL")
        self.ADMIN_NAMES: str = os.environ.get("ADMIN_NAMES") or config("ADMIN_NAMES")
        self.ADMIN_SURNAME: str = os.environ.get("ADMIN_SURNAME") or config("ADMIN_SURNAME")
        self.ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD") or config("ADMIN_PASSWORD")
        self.ADMIN_CELL: str = os.environ.get("ADMIN_CELL") or config("ADMIN_CELL")

        self.UTC_OFFSET = datetime.timedelta(hours=2)
        self.DATASTORE_TIMEOUT: int = 360  # seconds 6 minutes
        self.DATASTORE_RETRIES: int = 3  # total retries when saving to datastore

        self.IS_PRODUCTION: bool = True
        self.SECRET_KEY: str = os.environ.get("SECRET_KEY") or config("SECRET_KEY")
        self.DEBUG: bool = False
        self.RABBIT_MQ_URL: str = os.environ.get("RABBIT_MQ_URL") or config("RABBIT_MQ_URL")

        # NOTE : setting IS_PRODUCTION here - could find a better way of doing this rather
        # than depending on the OS
        if "Windows_NT" == os.environ.get("OS"):
            self.DEBUG = True
            self.IS_PRODUCTION = False
            self.ENV = "development"
            self.PROPAGATE_EXCEPTIONS: bool = True
            self.PRESERVE_CONTEXT_ON_EXCEPTION: bool = True
            self.EXPLAIN_TEMPLATE_LOADING: bool = False
            self.PREFERRED_URL_SCHEME: str = "http"
            self.TESTING: bool = True
            # TODO - set Cache to MEM_CACHE and then setup the server URI, applicable on version 2


config_instance: Config = Config()
# Note: Config is a singleton - this means it cannot be redeclared anywhere else
del Config
