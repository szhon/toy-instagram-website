"""REST API for posts."""
import flask
import insta485


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def post_like():
    """Like a post."""
    logname = insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )

    connection = insta485.model.get_db()
    postid = flask.request.args.get("postid")
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? " "AND postid = ?",
        (
            logname,
            postid,
        ),
    )
    exist = len(cur.fetchall())
    if exist != 0:
        raise insta485.model.InvalidUsage("Conflict", 409)
    cur = connection.execute(
        "INSERT INTO likes(owner, postid) " "VALUES (?, ?)", (logname, postid)
    )
    cur = connection.execute("SELECT last_insert_rowid() AS id")
    res = cur.fetchall()
    context = {"likeid": res[0]["id"], "url": f"/api/v1/likes/{res[0]['id']}/"}
    return (flask.jsonify(**context), 201)


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Delete a like on post of postid."""
    insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )
    connection = insta485.model.get_db()
    connection.execute("DELETE FROM likes WHERE likeid = ?", (likeid,))
    return ("", 204)
