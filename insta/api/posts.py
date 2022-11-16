"""REST API for posts."""
import hashlib
import flask
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_resource():
    """Get Resource."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": flask.request.path,
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/', methods=["GET"])
def get_posts_new():
    """Get New Posts."""
    connection = insta485.model.get_db()
    print("session", flask.session)
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)
        print('3')
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(username, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        username = flask.session['username']
    size = 10
    page = 0
    post_id_lte = -1
    first = True
    url = flask.request.path
    url_dict = flask.request.args.to_dict()
    print(url_dict)
    for key in url_dict:
        if first:
            url = url + "?" + key + "=" + url_dict[key]
            first = False
        else:
            url = url + "&" + key + "=" + url_dict[key]

    if 'size' in flask.request.args.to_dict():
        size = flask.request.args['size']
        # url = url + "size=" + size + "/"
        # first = False

    if 'page' in flask.request.args.to_dict():
        page = flask.request.args['page']
        # if(first):
        #     url = url + "page=" + page
        #     first = False
        # else:
        #     url = url + "&page=" + page
    if 'postid_lte' in flask.request.args.to_dict():
        post_id_lte = flask.request.args['postid_lte']
        # if(first):
        #     url = url + "postid_lte=" + post_id_lte
        #     first = False
        # else:
        #     url = url + "&postid_lte=" + post_id_lte
    return get_pagination(username, size, page, post_id_lte, url)


# /api/v1/posts/?postid_lte=N
# Return post urls and ids no newer than post id N
def get_pagination(username, size, page, post_id_lte, url):
    """Get Pagination."""
    connection = insta485.model.get_db()
    offset = int(page) * int(size)
    postids = []
    next_url = ""
    temp = []
    if int(page) < 0 or int(size) < 0:
        return flask.make_response('', 400)
    if post_id_lte == -1:
        cur1 = connection.execute(
            "SELECT postid FROM posts WHERE (owner IN "
            "(SELECT username2 FROM following WHERE username1 = ?) "
            "OR owner = ?) "
            "ORDER BY postid DESC "
            "LIMIT 1 "
            "OFFSET ? ",
            (username, username, offset,)

        )
        # print(cur1.fetchone()['postid'])
        temp = cur1.fetchone()

        print(type(temp))
        if temp is None:
            post_id_lte = 0
            postids = []
            next_url = ""
        else:
            post_id_lte = temp['postid']

    print("POSTIDLTE", post_id_lte)
    if temp is not None:
        print("HELLO")
        cur = connection.execute(
            "SELECT postid FROM posts WHERE postid <= ? AND (owner IN "
            "(SELECT username2 FROM following WHERE username1 = ?) "
            "OR owner = ?) "
            "ORDER BY postid DESC "
            "LIMIT ? "
            "OFFSET ? ",

            (post_id_lte, username, username, size, offset,)

            )

        postids = cur.fetchall()
        print("POSTIDS: ", postids)
        if len(postids) < int(size):
            next_url = ""
        else:
            page = int(len(postids) / int(size))
            next_url = "/api/v1/posts/?size=" + str(size) + "&page="\
                + str(page) + "&postid_lte=" + str(postids[0]["postid"])
        for postid in postids:
            postid["url"] = flask.request.path + str(postid["postid"]) + "/"

    context = {
        "next": next_url, "results": postids, "url": url
    }
    return flask.jsonify(**context)


def check_authentication(username, password, db_val):
    """Check Auth."""
    cur = db_val.execute(
        "SELECT password FROM users WHERE username != ?",
        (username, )
    )
    hashed_password = cur.fetchone()['password']
    cut = hashed_password.split('$')
    algorithm = cut[0]
    salt = cut[1]
    hashy = hashlib.new(algorithm)
    salty_password = salt + password
    hashy.update(salty_password.encode('utf-8'))
    password_hash = hashy.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if hashed_password == password_db_string:
        return True
    return False


def set_comment(connection, postid, logname):
    """Set Comment."""
    cur2 = connection.execute(
        "SELECT * FROM comments WHERE postid = ?",
        (postid, )
        )
    comments = []
    for comment_fetch in cur2.fetchall():
        comment = {}
        if comment_fetch['owner'] == logname:
            comment_fetch['lognameOwnsThis'] = True
            comment['lognameOwnsThis'] = comment_fetch['lognameOwnsThis']
        else:
            comment_fetch['lognameOwnsThis'] = False
            comment['lognameOwnsThis'] = comment_fetch['lognameOwnsThis']
        comment_fetch["ownerShowUrl"] = '/users/' +\
            comment_fetch['owner'] + "/"
        comment['ownerShowUrl'] = comment_fetch['ownerShowUrl']
        comment_fetch['url'] = '/api/v1/comments/' +\
            str(comment_fetch['commentid']) + "/"
        comment['url'] = comment_fetch['url']
        comment['text'] = comment_fetch['text']
        comment['owner'] = comment_fetch['owner']
        comment['commentid'] = comment_fetch['commentid']
        comments.append(comment)

    return comments


def set_likes(connection, postid, logname):
    """Set Likes."""
    cur3 = connection.execute(
        "SELECT * FROM likes WHERE postid = ?",
        (postid, )
        )
    likes_fetch = cur3.fetchall()
    likes = {}
    likeid = -1
    likes['lognameLikesThis'] = False
    for like in likes_fetch:
        if like['owner'] == logname:
            likes['lognameLikesThis'] = True
            likeid = like['likeid']
    if likeid == -1:
        likes['url'] = None
    else:
        likes['url'] = "/api/v1/likes/" + str(likeid) + "/"
    likes['numLikes'] = len(likes_fetch)

    return likes


@insta485.app.route('/api/v1/posts/<int:postid>/', methods=["GET"])
def get_one_postid(postid):
    """Get One Post ID."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)
        print('3')
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(logname, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        logname = flask.session['username']
    cur = connection.execute(
        "SELECT * FROM posts WHERE postid =?",
        (postid,)
        )
    posts = cur.fetchall()
    print(len(posts), posts, postid)
    if len(posts) != 1:
        return flask.make_response('', 404)
    for post in posts:
        post_show_url = "/posts/" + str(post["postid"]) + "/"
        img_url = '/uploads/' + post['filename']
        created = post['created']
        owner = post['owner']
        owner_show_url = '/users/' + post['owner']

    cur4 = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (owner, )
        )
    # ownerimgurl = cur4.fetchall()[0]
    context = {
        "comments": set_comment(connection, postid, logname),
        "comments_url": '/api/v1/comments/?postid=' + str(postid),
        "created": created, "imgUrl": img_url,
        "likes": set_likes(connection, postid, logname),
        "owner": owner,
        "ownerImgUrl": '/uploads/'+cur4.fetchall()[0]['filename'],
        "ownerShowUrl": owner_show_url+'/', "postShowUrl": post_show_url,
        "postid": postid, "url": flask.request.path
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=["POST"])
def post_likes_new():
    """Post New Likes."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)

        print('3')
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(logname, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        logname = flask.session['username']

    if 'postid' in flask.request.args.to_dict():
        l_postid = flask.request.args['postid']

        cur = connection.execute(
            "SELECT * FROM likes WHERE postid = ? AND owner = ?",
            (l_postid, logname, )
        )
        likes_already_exists = cur.fetchall()
        print("LENGTH", len(likes_already_exists), likes_already_exists)
        if len(likes_already_exists) == 1:
            res = {}
            res['likeid'] = likes_already_exists[0]['likeid']
            res['url'] = '/api/v1/likes/' +\
                str(likes_already_exists[0]['likeid']) + "/"
            return flask.make_response(res, 200)

        connection.execute(
            "INSERT INTO likes(owner, postid ) VALUES (?, ?)",
            (logname, l_postid, )
        )

    cur = connection.execute(
            "SELECT * FROM likes ORDER BY likeid DESC LIMIT 1 "
        )
    likes = cur.fetchall()[0]
    res = {}
    res['likeid'] = likes['likeid']
    res['url'] = '/api/v1/likes/' + str(likes['likeid']) + "/"

    return flask.make_response(res, 201)


@insta485.app.route('/api/v1/likes/<likeid>/', methods=["DELETE"])
def delete_like(likeid):
    """Delete Like."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)

        print('3')
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(logname, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        logname = flask.session['username']

    cur = connection.execute(
        "SELECT * FROM likes where likeid = ?",
        (likeid, )
    )

    likeids = cur.fetchall()

    if len(likeids) == 0:
        return flask.make_response('', 404)
    for like in likeids:
        if like['owner'] != logname:
            return flask.make_response('', 403)

    connection.execute(
            "DELETE FROM likes WHERE likeid = ? AND owner = ?",
            (likeid, logname, )
        )

    # don't return anything 204 OK status
    return flask.make_response('', 204)


@insta485.app.route('/api/v1/comments/', methods=["POST"])
def post_comment():
    """Post Comment."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)

        print('3')
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(logname, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        logname = flask.session['username']

    if 'postid' in flask.request.args.to_dict():
        print("made it")
        c_postid = flask.request.args['postid']
        # logname = flask.request.authorization['username']
        text = flask.request.json['text']
        print(logname, text, c_postid)
        connection.execute(
            "INSERT INTO comments(owner, text, postid ) "
            "VALUES (?, ?, ?) ",
            (logname, text, c_postid, )
        )

        cur = connection.execute(
            "SELECT * FROM comments ORDER BY commentid DESC LIMIT 1 "
        )
        comment = cur.fetchall()[0]
        res = {}
        res['commentid'] = comment['commentid']
        if comment['owner'] == logname:
            res['lognameOwnsThis'] = True
        else:
            res['lognameOwnsThis'] = False
        res['owner'] = comment['owner']
        res['ownerShowUrl'] = '/users/' + comment['owner'] + '/'
        res['text'] = comment['text']
        res['url'] = '/api/v1/comments/' + str(comment['commentid']) + "/"
        print("REACHED END")

    return flask.make_response(res, 201)


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete comment based on commentid."""
    connection = insta485.model.get_db()
    # HTTP Basic Access Authentication
    if 'username' not in flask.session:
        if flask.request.authorization is None:
            print('1')
            return flask.make_response('', 403)

        print('3')
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not check_authentication(logname, password, connection):
            print("4")
            return flask.make_response('', 403)
    else:
        print('2')
        logname = flask.session['username']

    # check commentid exists and user is owener
    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ? ",
        (commentid, )
    )
    user = cur.fetchone()
    # commentid does not exists
    if user is None:
        return flask.make_response('', 404)
    # user doesn't own comment
    if user['owner'] != logname:
        return flask.make_response('', 403)
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid, )
    )
    return flask.make_response('', 204)
