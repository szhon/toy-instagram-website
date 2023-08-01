"""
Insta485 uploads view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route("/uploads/<path:filename>")
def download_file(filename):
    """Get image from database."""
    if flask.session.get("username") is None:
        flask.abort(403, "Not logged in but tries to get files")
    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )
