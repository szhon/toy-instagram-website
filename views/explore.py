"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
import insta485


@insta485.app.route("/explore/", methods=["GET"])
def show_explore():
    """Display explore page."""
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session.get("username")

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username, u.filename as user_img_url "
        "FROM users u "
        "WHERE u.username NOT IN "
        "(SELECT username2 FROM following "
        "WHERE username1 = '" + logname + "') "
        "AND u.username NOT IN "
        "(SELECT username FROM users "
        "WHERE username = '" + logname + "')"
    )
    res = cur.fetchall()
    context = {"logname": logname, "not_following": res}

    # breakpoint()
    return flask.render_template("explore.html", **context)
