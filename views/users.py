"""
Insta485 users view.

URLs include:
/users/<user_url_slug>/
"""
import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/", methods=["GET"])
def show_user(user_url_slug):
    """Display user."""
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    connection = insta485.model.get_db()

    logname = flask.session.get("username")
    context = {"logname": logname, "username": user_url_slug}

    # fullname
    sql = (
        "SELECT DISTINCT fullname "
        "FROM users "
        "WHERE username = '" + user_url_slug + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        flask.abort(404)
    context["fullname"] = res[0]["fullname"]

    # logname_follows_username
    sql = (
        "SELECT username1, username2 FROM following WHERE username1 = '"
        + logname
        + "' AND username2 = '"
        + user_url_slug
        + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        context["logname_follows_username"] = False
    else:
        context["logname_follows_username"] = True

    # following
    sql = (
        "SELECT COUNT(f.username2) AS following "
        "FROM following f WHERE f.username1 = '" + user_url_slug + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        context["following"] = 0
    else:
        context["following"] = res[0]["following"]

    # followers
    sql = (
        "SELECT COUNT(f.username1) AS followers "
        "FROM following f WHERE f.username2 = '" + user_url_slug + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        context["followers"] = 0
    else:
        context["followers"] = res[0]["followers"]

    # post
    sql = (
        "SELECT DISTINCT p.postid, p.filename AS img_url FROM posts p "
        "WHERE p.owner = '" + user_url_slug + "' ORDER BY p.postid"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    context["total_posts"] = len(res)
    context["posts"] = res

    return flask.render_template("user.html", **context)


@insta485.app.route("/users/<user_url_slug>/followers/", methods=["GET"])
def show_user_follower(user_url_slug):
    """Display user follower."""
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session.get("username")
    context = {"logname": logname, "username": user_url_slug}

    connection = insta485.model.get_db()
    sql = (
        "SELECT DISTINCT username "
        "FROM users "
        "WHERE username = '" + user_url_slug + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        flask.abort(404)
    sql = (
        "SELECT u.username, u.filename AS user_img_url, "
        "f2.username1 AS logname_follows_username "
        "FROM users u "
        "INNER JOIN following f1 "
        "ON f1.username2 = '" + user_url_slug
        + "' AND f1.username1 = u.username "
        "LEFT JOIN following f2 "
        "ON f2.username1 = '" + logname + "' AND f2.username2 = u.username"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    context["followers"] = res
    return flask.render_template("followers.html", **context)


@insta485.app.route("/users/<user_url_slug>/following/", methods=["GET"])
def show_user_following(user_url_slug):
    """Display user following."""
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session.get("username")
    context = {"logname": logname, "username": user_url_slug}

    connection = insta485.model.get_db()
    sql = (
        "SELECT DISTINCT username "
        "FROM users "
        "WHERE username = '" + user_url_slug + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        flask.abort(404)

    sql = (
        "SELECT u.username, u.filename AS user_img_url, "
        "f2.username1 AS logname_follows_username "
        "FROM users u "
        "INNER JOIN following f1 "
        "ON f1.username1 = '" + user_url_slug
        + "' AND f1.username2 = u.username "
        "LEFT JOIN following f2 "
        "ON f2.username1 = '" + logname
        + "' AND f2.username2 = u.username"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    context["following"] = res
    return flask.render_template("following.html", **context)
