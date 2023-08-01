"""
Insta485 login view.

URLs include:
/accounts/
/accounts/login
"""
import flask
import insta485


@insta485.app.route("/likes/", methods=["POST"])
def exe_likes_post():
    """
    Execute likes POST request.

    (operation = like/unlike)
    """
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    connection = insta485.model.get_db()
    if flask.request.form.get("operation") == "like":
        sql = "SELECT * FROM likes WHERE " "owner = '" + flask.session.get(
            "username"
        ) + "' AND postid = " + str(flask.request.form.get("postid"))
        cur = connection.execute(sql)
        exist = len(cur.fetchall())
        if exist != 0:
            flask.abort(409)
        sql = (
            "INSERT INTO likes(owner, postid) "
            "VALUES ('"
            + flask.session.get("username")
            + "', "
            + str(flask.request.form.get("postid"))
            + ")"
        )
        cur = connection.execute(sql)
    elif flask.request.form.get("operation") == "unlike":
        cur = connection.execute(
            "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
            (flask.session.get("username"), flask.request.form.get("postid"))
        )
        exist = len(cur.fetchall())
        if exist == 0:
            flask.abort(409)
        sql = "DELETE FROM likes " "WHERE owner = '" + flask.session.get(
            "username"
        ) + "' AND postid = " + str(flask.request.form.get("postid"))
        cur = connection.execute(sql)
    else:
        flask.abort(400)
    url = insta485.model.url_format(
        flask.request.args.get("target"), "show_index"
    )
    return flask.redirect(url)
