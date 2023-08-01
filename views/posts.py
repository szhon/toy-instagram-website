"""
Insta485 posts view.

URLs include:
/posts/<postid_url_slug>/
"""
import flask
import arrow
import insta485


@insta485.app.route("/posts/<postid_url_slug>/", methods=["GET"])
def show_post(postid_url_slug):
    """Display post page."""
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session.get("username")

    connection = insta485.model.get_db()
    sql = (
        "SELECT p.postid, p.filename AS img_url, p.owner, p.created "
        "AS timestamp, u.filename AS owner_img_url, "
        "COUNT(l.likeid) AS likes, l2.owner AS like_action "
        "FROM posts p "
        "INNER JOIN users u "
        "ON p.owner = u.username AND p.postid = " + str(postid_url_slug) + " "
        "LEFT JOIN likes l "
        "ON l.postid = p.postid "
        "LEFT JOIN likes l2 "
        "ON p.postid = l2.postid AND l2.owner = '" + logname + "'"
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        flask.abort(404)
    context = res[0]
    context["logname"] = logname
    context["postid"] = postid_url_slug
    time = context["timestamp"]
    timeformat = "YYYY-MM-DD HH:mm:ss"
    # print(time, arrow.get(time, timeformat).humanize())
    context["timestamp"] = arrow.get(time, timeformat).humanize()
    if context.get("like_action") is None:
        context["like_action"] = "like"
    else:
        context["like_action"] = "unlike"

    sql = (
        "SELECT c.commentid, c.text, c.owner "
        "FROM comments c "
        "WHERE c.postid = " + str(postid_url_slug) + " "
        "ORDER BY c.commentid "
    )
    cur = connection.execute(sql)
    res = cur.fetchall()
    context["comments"] = res
    # breakpoint()
    return flask.render_template("posts.html", **context)


@insta485.app.route("/posts/", methods=["POST"])
def exe_posts_post():
    """
    Execute post POST request.

    opeartion=(create/delete)
    """
    if flask.session.get("username") is None:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session.get("username")

    url = flask.request.args.get("target")
    if url is None:
        url = flask.url_for("show_user", user_url_slug=logname)

    if flask.request.form.get("operation") == "create":
        fileobj = flask.request.files.get("file")
        if not fileobj:
            flask.abort(400, "Create post with empty file")

        uuid_basename = insta485.model.create_img(fileobj)
        connection = insta485.model.get_db()
        sql = (
            "INSERT INTO posts(filename, owner)"
            "VALUES ('" + uuid_basename + "', '" + logname + "')"
        )
        cur = connection.execute(sql)
    elif flask.request.form.get("operation") == "delete":
        connection = insta485.model.get_db()
        sql = "SELECT filename, owner FROM posts WHERE postid = " + str(
            flask.request.form.get("postid")
        )
        cur = connection.execute(sql)
        res = cur.fetchall()
        if len(res) == 0:
            return flask.redirect(url)
        if res[0]["owner"] != logname:
            flask.abort(403, "Tries to delete post not owned")

        insta485.model.delete_img(res[0]["filename"])
        sql = "DELETE FROM posts WHERE postid = " + str(
            flask.request.form.get("postid")
        )
        cur = connection.execute(sql)
    else:
        flask.abort(400)
    return flask.redirect(url)
