"""REST API for posts."""
import flask
import insta485


def post_view_para(request):
    """Set parameters for viewing page."""
    size = request.args.get("size", default=10, type=int)
    page = request.args.get("page", default=0, type=int)
    postid_lte = request.args.get("postid_lte", type=int)
    postid_lte_sql = ""

    if (
        (size is not None and size < 0)
        or (page is not None and page < 0)  # or
        # (postid_lte is not None and postid_lte < 0)
    ):
        raise insta485.model.InvalidUsage(
            message="Bad Request", status_code=400
        )

    if postid_lte is not None:
        postid_lte_sql = f"AND p.postid <= {postid_lte} "

    return size, page, postid_lte, postid_lte_sql


def process_post(connection, logname, post):
    """Process post fromat."""
    post['imgUrl'] = f"/uploads/{post['imgUrl']}"
    post['ownerImgUrl'] = f"/uploads/{post['ownerImgUrl']}"
    post['ownerShowUrl'] = f"/users/{post['owner']}/"
    post['postShowUrl'] = f"/posts/{post['postid']}/"
    post['url'] = f"/api/v1/posts/{post['postid']}/"
    likes = {"lognameLikesThis": False, "numLikes": 0, "url": None}

    if post.get("likes") is not None:
        likes['numLikes'] = post.get("likes")

    if post.get("likeid") is not None:
        likes['lognameLikesThis'] = True

    if likes['lognameLikesThis']:
        likes['url'] = f"/api/v1/likes/{post['likeid']}/"

    del post['likeid']

    post['likes'] = likes

    cur = connection.execute(
        "SELECT DISTINCT c.commentid, c.owner, c.text FROM comments c "
        "WHERE c.postid = ? ORDER BY c.commentid",
        (post['postid'],),
    )
    post['comments'] = cur.fetchall()
    for comment in post['comments']:
        comment['lognameOwnsThis'] = logname == comment['owner']
        comment['ownerShowUrl'] = f"/users/{comment['owner']}/"
        comment['url'] = f"/api/v1/comments/{comment['commentid']}/"


@insta485.app.route("/api/v1/")
def get_links():
    """Return links."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return (flask.jsonify(**context), 200)


@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/", methods=['GET'])
def get_post(postid_url_slug):
    """Return post on postid."""
    logname = insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT DISTINCT p.postid, p.filename AS imgUrl, p.owner, "
        "p.created, u.filename AS ownerImgUrl, t.likes, l.likeid "
        "FROM posts p "
        "INNER JOIN following f "
        "ON p.postid = ? "
        "INNER JOIN users u "
        "ON u.username =  p.owner "
        "LEFT JOIN (SELECT COUNT(*) AS likes, "
        "postid FROM likes GROUP BY postid ) t "
        "ON p.postid = t.postid "
        "LEFT JOIN likes l "
        "ON p.postid = l.postid AND l.owner = ? "
        "ORDER BY p.postid DESC ",
        (
            postid_url_slug,
            logname,
        ),
    )
    post = cur.fetchall()
    if len(post) == 0:
        raise insta485.model.InvalidUsage(message="Not Found", status_code=404)
    post = post[0]

    process_post(connection, logname, post)

    context = post
    context['url'] = flask.request.path
    return (flask.jsonify(**context), 200)


@insta485.app.route("/api/v1/posts/")
def get_posts():
    """Return the newest posts. 10 if not specified."""
    logname = insta485.model.authorization_check(
        flask.session, flask.request.authorization
    )

    size, page, postid_lte, postid_lte_sql = post_view_para(flask.request)

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT DISTINCT p.postid, p.filename AS imgUrl, p.owner, "
        "p.created, u.filename AS ownerImgUrl, t.likes, l.likeid "
        "FROM posts p "
        "INNER JOIN following f "
        "ON ((f.username2 = p.owner AND f.username1 = ?) "
        "OR p.owner = ?) " + postid_lte_sql + "INNER JOIN users u "
        "ON u.username =  p.owner "
        "LEFT JOIN (SELECT COUNT(*) AS likes, "
        "postid FROM likes GROUP BY postid ) t "
        "ON p.postid = t.postid "
        "LEFT JOIN likes l "
        "ON p.postid = l.postid AND l.owner = ? "
        "ORDER BY p.postid DESC "
        "LIMIT ? OFFSET ?",
        (logname, logname, logname, size, size * page),
    )
    posts = cur.fetchall()

    for i, post in enumerate(posts):
        if i == 0 and postid_lte is None:
            postid_lte = post['postid']
        process_post(connection, logname, post)

    next_url = ""
    if len(posts) == size:
        next_url = flask.request.path
        next_url += f"?size={size}&page={page+1}&postid_lte={postid_lte}"

    # Add database info to context
    url = flask.request.path
    if flask.request.query_string.decode():
        url += "?" + flask.request.query_string.decode()
    context = {"next": next_url, "results": posts, "url": url}
    return (flask.jsonify(**context), 200)
