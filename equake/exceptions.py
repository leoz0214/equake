"""Exceptions to be raised and caught in the library."""
from urllib import error


class EquakeException(Exception):
    """Base exception for all library-specific exceptions."""


class RequestError(error.URLError, EquakeException):
    """Something went wrong with the request."""


class HTTPError(RequestError):
    """
    Error raised when something goes wrong with the HTTP request to the
    USGS Earthquake API. Likely a server/connection issue.
    """
