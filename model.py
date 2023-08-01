"""Insta485 model (database) API."""
import sqlite3
import uuid
import hashlib
import pathlib
import os
import flask
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if "sqlite_db" not in flask.g:
        db_filename = insta485.app.config["DATABASE_FILENAME"]
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop("sqlite_db", None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


class InvalidUsage(Exception):
    """InvalidUsage exception class."""

    def __init__(self, message, status_code):
        """Class init."""
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """To dictionary."""
        error = {"message": self.message, "status_code": self.status_code}
        return error


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle error."""
    error = error.to_dict()
    return (error, error["status_code"])


def compare_password(form_password, saved_password):
    """Compare password."""
    saved_password = saved_password[0]["password"].split("$")
    hash_obj = hashlib.new(saved_password[0])
    password_salted = saved_password[1] + form_password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    return password_hash != saved_password[2]


def authorization_check(session, authorization):
    """Check authorization."""
    if session.get("username") is None:
        if authorization is None:
            # flask.abort(403)
            raise InvalidUsage("Forbidden", 403)
        username = authorization["username"]
        password = authorization["password"]
        check_required_fields([username, password])
        connection = get_db()
        cur = connection.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        )
        saved_password = cur.fetchall()
        if (
            len(saved_password) == 0
            or compare_password(password, saved_password)
        ):
            raise InvalidUsage("Forbidden", 403)
        return username
    return session.get("username")


def check_required_fields(required_fields):
    """Check required fields and abort(400) if empty."""
    for item in required_fields:
        if not item:
            flask.abort(403)


def url_format(url, target):
    """Get correct url."""
    if url is None:
        url = flask.url_for(target)
    return url


def create_img(fileobj):
    """Save image file to database."""
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    return uuid_basename


def delete_img(filename):
    """Delete image file from database."""
    path = insta485.app.config["UPLOAD_FOLDER"] / filename
    os.remove(path)
