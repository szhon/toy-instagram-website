"""REST API for posts."""
import flask
import insta485


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def post_comment():
    """Create a comment on post geiven postid."""
    logname = insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )

    connection = insta485.model.get_db()
    postid = flask.request.args.get("postid")
    text = flask.request.json["text"]
    cur = connection.execute(
        "INSERT INTO comments(owner, postid, text) " "VALUES (?, ?, ?)",
        (logname, postid, text),
    )
    cur = connection.execute("SELECT last_insert_rowid() AS id")
    res = cur.fetchall()
    context = {
        "commentid": res[0]["id"],
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": f"/users/{logname}/",
        "text": text,
        "url": f"/api/v1/comments/{res[0]['id']}/",
    }
    return (flask.jsonify(**context), 201)


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete a like on post of postid."""
    insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid,)
        )
    return ("", 204)
