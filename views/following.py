"""
Insta485 login view.

URLs include:
/accounts/
/accounts/login
"""
import flask
import insta485


@insta485.app.route("/following/", methods=["POST"])
def exe_following_post():
    """
    Execute following POST request.

    operation = (follow/unfollow)
    """
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    url = flask.request.args.get("target")
    url = insta485.model.url_format(url, "show_index")

    logname = flask.session.get("username")
    username = flask.request.form.get("username")
    connection = insta485.model.get_db()
    sql = (
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username1 = '" + logname + "' "
        "AND username2 = '" + username + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    # breakpoint()
    if flask.request.form.get("operation") == "follow":
        if len(res) != 0:
            flask.abort(409, "Tries to follow an already followed user")

        sql = (
            "INSERT INTO following(username1, username2) "
            "VALUES ('" + logname + "', '" + username + "')"
        )
        cur = connection.execute(sql)

    elif flask.request.form.get("operation") == "unfollow":
        if len(res) == 0:
            flask.abort(409, "Tries to unfollow a not following user")

        sql = (
            "DELETE FROM following "
            "WHERE username1 = '" + logname + "' "
            "AND username2 = '" + username + "'"
        )
        cur = connection.execute(sql)
        res = cur.fetchall()
    else:
        flask.abort(400, "WRONG OPERATION FOR FOLLOWING")
    return flask.redirect(url)
