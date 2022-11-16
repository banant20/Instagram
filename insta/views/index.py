"""
Insta485 index (main) view.

URLs include:
/
"""
import hashlib
import pathlib
import uuid
import os
import arrow
import flask
from flask import send_from_directory
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    cur = connection.execute(
        "SELECT * FROM posts WHERE owner IN "
        "(SELECT username2 FROM following WHERE username1 = ?)"
        " OR owner = ?"
        "ORDER BY postid DESC",
        (logname, logname, )
        )
    posts = cur.fetchall()
    print(posts)
    for a_post in posts:
        cur2 = connection.execute(
            "SELECT * FROM likes WHERE ? = likes.postid ",
            (a_post['postid'],)
        )
        likes = cur2.fetchall()
        print("likes")
        print(likes)
        a_post['likes'] = likes
        a_post['count'] = len(likes)
        cur3 = connection.execute(
            "SELECT * FROM comments WHERE ? = comments.postid "
            "ORDER by commentid ASC ",
            (a_post['postid'],)
        )
        comments = cur3.fetchall()
        print("comments")
        print(comments)
        a_post['comments'] = comments
        cur4 = connection.execute(
            "SELECT filename FROM users WHERE ? = users.username",
            (a_post["owner"], )
        )
        temp_profile = cur4.fetchall()
        profile = temp_profile[0]["filename"]
        print(profile)
        a_post['profile'] = profile
        # arrow.get(post['created'])
        utc = arrow.get(a_post['created']).humanize()
        a_post['created'] = utc
        a_post["liked"] = False
        for like in likes:
            if like["owner"] == logname:
                a_post["liked"] = True
                break
    print("all posts")
    print(posts)
    # posts = cur.fetchall()
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)
    # return '''
    # Logged in as {}
    # '''.format(logname)


@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download File."""
    if 'username' not in flask.session:
        return flask.abort(403)
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename)


@insta485.app.route('/users/<username>/', methods=['GET'])
def users(username):
    """Users."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT ALL username2 FROM following WHERE username1 = ?",
        (username,)
    )
    following0 = cur.fetchall()
    cur2 = connection.execute(
        "SELECT * FROM posts WHERE owner =?",
        (username,)
    )
    posts = cur2.fetchall()
    cur3 = connection.execute(
        "SELECT ALL username1 FROM following WHERE username2 =?",
        (username, )
    )
    cur4 = connection.execute(
        "SELECT ALL username2 FROM following WHERE username1 =?",
        (flask.session['username'], )
    )
    # logname_following = cur4.fetchall()
    logname_list = []
    for dict1 in cur4.fetchall():
        logname_list.append(dict1['username2'])
    followers1 = cur3.fetchall()
    followers_list = []
    for dict1 in followers1:
        followers_list.append(dict1['username1'])
    # for follower in followers:
    #     if (follower == logname):
    #         follows = 1
    #         break
    follows = False
    if username in logname_list:
        follows = True
    cur4 = connection.execute(
        "SELECT fullname, filename FROM users WHERE username = ?",
        (username, )
    )
    users1 = cur4.fetchall()
    context = {"num_posts": len(posts), "posts": posts,
               "num_following": len(following0),
               "num_followers": len(followers1),
               "username": username,
               "logname": flask.session['username'],
               "logname_follows_username": follows,
               "users": users1}
    return flask.render_template("user.html", **context)
# susername1 follows username2


@insta485.app.route('/users/<username>/followers/', methods=["GET"])
def followers(username):
    """Username Followers."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username in "
        "(SELECT username1 FROM following WHERE username2 = ?) ",
        (username, )
    )
    followers2 = cur.fetchall()
    # figure out who logname follows
    cur2 = connection.execute(
        "SELECT  username2 FROM following WHERE username1 =?",
        (logname, )
    )
    logname_following = cur2.fetchall()
    logname_list = []
    for dict3 in logname_following:
        logname_list.append(dict3['username2'])
    for follower in followers2:
        if follower["username"] in logname_list:
            follower["follows"] = True
        else:
            follower["follows"] = False
    context = {"followers": followers2, "logname": logname, "param": username}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<username>/following/', methods=["GET"])
def following(username):
    """Username Following."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username in "
        "(SELECT username2 FROM following WHERE username1 = ?) ",
        (username, )
    )
    following1 = cur.fetchall()
    # figure out who logname follows
    cur2 = connection.execute(
        "SELECT username2 FROM following WHERE username1 =?",
        (logname, )
    )
    logname_following = cur2.fetchall()
    print("logname_following", logname_following)
    logname_list = []
    for dict4 in logname_following:
        logname_list.append(dict4['username2'])
    for follow in following1:
        if follow["username"] in logname_list:
            follow["follows"] = True
        else:
            follow["follows"] = False
    # logname_following = cur2.fetchall()
    print("updated following: ", following1)
    context = {"following": following1, "logname": logname, "param": username}
    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/', methods=["GET"])
def explore():
    """Explore Page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users"
    )
    users2 = cur.fetchall()
    cur2 = connection.execute(
        "SELECT username2 FROM following WHERE username1 =?",
        (logname, )
    )
    info = cur2.fetchall()
    logname_following = []
    for dict5 in info:
        logname_following.append(dict5['username2'])
    print(logname_following)
    explore1 = []
    for user in users2:
        if user["username"] not in logname_following\
         and user['username'] != logname:
            explore1.append(user)
    print("explore", explore1)
    context = {"users": explore1, "logname": logname}
    return flask.render_template("explore.html", **context)


# flask request arguments
# operations for post
@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Show Login."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Show A Page."""
    flask.session.pop("username")
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def post(postid_url_slug):
    """Post ID Redirect."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    # logname = 'awdeorio'
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes WHERE likes.postid = ?",
        (postid_url_slug, )
    )
    cur2 = connection.execute(
        "SELECT * FROM comments WHERE comments.postid = ?",
        (postid_url_slug, )
    )
    cur3 = connection.execute(
        "SELECT * FROM posts WHERE posts.postid = ?",
        (postid_url_slug, )
    )
    cur4 = connection.execute(
        "SELECT * FROM users WHERE username "
        "IN (SELECT owner FROM posts WHERE postid = ?) ",
        (postid_url_slug)
    )
    users3 = cur4.fetchall()
    likes = cur.fetchall()
    # print(likes)
    likes_list = []
    for dict6 in likes:
        likes_list.append(dict6["owner"])
    # print('logname: ', logname)
    print("likes list: ", likes_list)
    liked = bool(flask.session['username'] in likes_list)
    # if flask.session['username'] in likes_list:
    #     liked = True
    # else:
    #     liked = False
    print('liked: ', liked)
    comments = cur2.fetchall()
    # print(comments)
    posts = cur3.fetchall()
    for post0 in posts:
        post0['created'] = arrow.get(post0['created']).humanize()
    context = {"logname": flask.session['username'], "users": users3,
               "likes": len(likes), "liked": liked,
               "comments": comments, "posts": posts}
    return flask.render_template("post.html", **context)


@insta485.app.route('/accounts/create/', methods=["GET"])
def create():
    """Create."""
    if 'username' not in flask.session:
        return flask.render_template("create.html")
    return flask.redirect(flask.url_for('show_edit'))


@insta485.app.route('/accounts/edit/', methods=["GET"])
def show_edit():
    """Edit Profile."""
    if 'username' not in flask.session:
        return flask.render_template("login.html")
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT fullname, email, username, "
        "filename FROM users WHERE users.username = ? ",
        (logname, )
    )
    users4 = cur.fetchall()
    context = {"users": users4, "logname": logname}
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/', methods=['GET'])
def change_password():
    """Change Password."""
    if 'username' not in flask.session:
        return flask.render_template("login.html")
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('password.html', **context)


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Delete Password."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('delete.html', **context)


def post_account_login(request):
    """Post Account Login."""
    connection = insta485.model.get_db()
    username = str(request.form.get('username'))
    password = str(request.form.get('password'))
    print(username)
    print(password)
    if username == '' or password == '':
        flask.abort(400)
    # GET username and password
    cur = connection.execute(
        "SELECT username, password FROM users WHERE username = ?",
        (username,)
    )
    cur2 = connection.execute(
        "SELECT * from users",
    )
    all1 = cur2.fetchall()
    print(all1)
    login = cur.fetchall()
    print(len(login))
    print(login)
    if len(login) == 0:
        flask.abort(403)
    # Encrypt Password
    split = login[0]['password'].split('$')
    algorithm = split[0]  # hashed w in database
    salt = split[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    # print('info', login[0], password, password_db_string)
    if login[0]['username'] == username and\
       login[0]['password'] == password_db_string:
        print("in database")
        flask.session['username'] = username
    else:
        flask.abort(403)
        # access target query based on request url
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


def post_delete_account():
    """Delete Account."""
    if 'username' not in flask.session:
        flask.abort(403)
    logname = flask.session['username']
    connection = insta485.model.get_db()
    # remove disk
    # find path where profile pic was stored and delete
    cur = connection.execute(
        'SELECT filename, username from users WHERE username =?',
        (logname,)
    )
    info = cur.fetchall()[0]
    # os.remove(filename)
    filename = info["filename"]
    print('filename: ', filename)
    print('folder: ', insta485.app.config['UPLOAD_FOLDER'])
    file_path = (insta485.app.config['UPLOAD_FOLDER']/filename)
    result = pathlib.Path(file_path)
    print('file path: ', file_path)
    os.remove(result)
    cur2 = connection.execute(
        "SELECT ALL filename, owner from posts WHERE owner = ?",
        (logname,)
    )
    post_info = cur2.fetchall()
    filenames = []
    print('post_info: ', post_info)
    for info in post_info:
        print('info: ', info)
        filenames.append(info['filename'])
    for filename in filenames:
        file_path = (insta485.app.config['UPLOAD_FOLDER']/filename)
        result = pathlib.Path(file_path)
        print('file path: ', file_path)
        os.remove(result)
    connection.execute(
        "DELETE from users WHERE username=? ",
        (logname,)
    )
    print("in delete")
    flask.session.pop("username")
    # return flask.redirect(flask.url_for('create'))
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


def post_edit_account(request):
    """Edit Account."""
    # print("redirecting to edit_account")
    # return flask.redirect(flask.url_for('edit_account'))
    if 'username' not in flask.session:
        flask.abort(403)
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    fileobj = request.files["file"]
    if fullname == '' or email == '':
        print("hey 400 1")
        flask.abort(400)
    print("file:", fileobj)
    connection = insta485.model.get_db()
    print("FILEOBJ: ", fileobj.filename)
    if fileobj.filename == '':
        print("INCORRECT")
        connection.execute(
            "UPDATE users SET fullname =?, email =? "
            "WHERE username =?",
            (fullname, email, flask.session['username'],)
        )
    else:
        cur2 = connection.execute(
            "SELECT ALL filename, username from users WHERE username = ?",
            (flask.session['username'], )
        )
        user_info = cur2.fetchall()
        filenames = []
        for info in user_info:
            filenames.append(info['filename'])
        for info in filenames:
            file_path = (insta485.app.config['UPLOAD_FOLDER']/info)
            result = pathlib.Path(file_path)
        os.remove(result)
        filename = fileobj.filename
        # Compute base name (filename without directory).
        # We use a UUID to avoid clashes with existing files,
        # and ensure that the name is compatible with the
        # filesystem.
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{uuid.uuid4().hex}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "UPDATE users SET fullname = ?, email = ?, "
            "filename = ? WHERE username = ? ",
            (fullname, email, uuid_basename, flask.session['username'],)
        )
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


def post_create_account(request):
    """Create Account."""
    connection = insta485.model.get_db()
    flask.session['username'] = request.form['username']
    if request.form.get('password') == "":
        flask.abort(400)
    if request.form.get('fullname') == "":
        flask.abort(400)
    if request.form.get('email') == "":
        flask.abort(400)
    if request.form['username'] == "" or request.files["file"].filename == "":
        flask.abort(400)
    duplicate_check = connection.execute(
            "SELECT * FROM users"
        )
    dup_check_list = []
    for dict7 in duplicate_check:
        dup_check_list.append(dict7['username'])
    if request.form['username'] in dup_check_list:
        flask.abort(409)
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(request.files["file"].filename).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    request.files["file"].save(path)
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + request.form.get('password')
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    print(password_db_string)
    connection.execute(
            "INSERT INTO "
            "users(username, fullname, filename, email, password) "
            "VALUES (?, ?, ?,?,?) ",
            (request.form['username'],
             request.form.get('fullname'), uuid_basename,
             request.form.get('email'),
             password_db_string, )
        )
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


def post_update_password(request):
    """Update Password."""
    if 'username' not in flask.session:
        flask.abort(403)
    old_password = request.form.get('password')
    new_password1 = request.form.get('new_password1')
    new_password2 = request.form.get('new_password2')
    if old_password == '' or new_password1 == '' or new_password2 == '':
        flask.abort(400)
    if new_password1 != new_password2:
        flask.abort(401)
    # verify password matches hashed password in databaseFilename
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username, password FROM users WHERE username =?",
        (flask.session['username'], )
    )
    login = cur.fetchall()
    split = login[0]['password'].split('$')
    algorithm = split[0]  # hashed w in database
    salt = split[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + old_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    print('password from db: ', login[0]['password'])
    if login[0]['password'] != password_db_string:
        flask.abort(403)
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + new_password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string1 = "$".join([algorithm, salt, password_hash])
    connection.execute(
            "UPDATE users SET password =? WHERE username =?",
            (password_db_string1, flask.session['username'],)
        )
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


@insta485.app.route('/accounts/', methods=['POST'])
def show_accounts():
    """Accounts."""
    print("enter show accounts")
    operation = flask.request.form.get('operation')
    if operation == 'login':
        return post_account_login(flask.request)
    if operation == 'delete':
        return post_delete_account()
    if operation == 'edit_account':
        return post_edit_account(flask.request)
    if operation == 'create':
        return post_create_account(flask.request)
    if operation == 'update_password':
        return post_update_password(flask.request)
    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/following/', methods=["POST"])
def post_following():
    """POST Method for Following."""
    operation = flask.request.form.get('operation')
    logname = flask.session['username']
    print('operation')
    if operation == 'follow':
        connection = insta485.model.get_db()
        cur2 = connection.execute(
            "SELECT ALL username2 FROM following WHERE username1 =?",
            (logname,)
        )
        all_following = cur2.fetchall()
        for dict8 in all_following:
            if dict8['username2'] == flask.request.form.get('username'):
                flask.abort(409)
        connection.execute(
            "INSERT INTO following(username1, username2 ) VALUES (?, ?)",
            (logname, flask.request.form.get('username'), )
        )
    if operation == 'unfollow':
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT ALL username2 FROM following WHERE username1 = ?",
            (logname,)
        )
        following2 = cur.fetchall()
        following_list = []
        for dict9 in following2:
            following_list.append(dict9['username2'])
        if flask.request.form.get('username') not in following_list:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following WHERE username2 = ? AND username1 = ?",
            (flask.request.form.get('username'), logname, )
        )
    # print("flask redirect", flask.request.args.get('target'))
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


@insta485.app.route('/comments/', methods=["POST"])
def post_comments():
    """POST Comments."""
    operation = flask.request.form.get('operation')
    logname = flask.session['username']
    connection = insta485.model.get_db()

    if operation == 'create':
        if len(flask.request.form.get('text')) == 0:
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments(owner, text, postid ) "
            "VALUES (?, ?, ?) ",
            (logname, flask.request.form.get('text'),
             flask.request.form.get('postid'), )
        )
        # cur = connection.execute(
        #     "SELECT * FROM comments where postid = ?",
        #     (flask.request.form.get('postid'))
        # )
        # comment_info = cur.fetchall()
        # print(comment_info)
    if operation == 'delete':
        cur = connection.execute(
            "SELECT owner, commentid from comments where commentid =?",
            (flask.request.form.get('commentid'),)
        )
        owner = cur.fetchall()[0]
        if owner['owner'] != logname:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (flask.request.form.get('commentid'), )
        )
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.to_dict()['target'])


@insta485.app.route('/likes/', methods=["POST"])
def post_likes():
    """POST Likes."""
    operation = flask.request.form.get('operation')
    logname = flask.session['username']
    print("op: ", operation)
    connection = insta485.model.get_db()
    cur2 = connection.execute(
        "SELECT * from likes WHERE postid = ? AND owner = ?",
        (flask.request.form.get('postid'), logname, )
        )
    likes = cur2.fetchall()
    # print("user's likes: ", likes)

    if operation == 'like':
        print("likes", likes)
        print("likes length", len(likes))
        if len(likes) == 1:
            flask.abort(409)

        connection.execute(
            "INSERT INTO likes(owner, postid ) VALUES (?, ?)",
            (logname, flask.request.form.get('postid'), )
        )
    # error check for unliking a post that is already unliked
    if operation == 'unlike':
        if len(likes) == 0:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE postid = ? AND owner = ?",
            (flask.request.form.get('postid'), logname, )
        )
    # if (flask.request.args.get('target') is None):
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args.to_dict()['target'])


@insta485.app.route('/posts/', methods=["POST"])
def post_posts():
    """POST Posts."""
    operation = flask.request.form.get('operation')
    logname = flask.session['username']
    connection = insta485.model.get_db()
    # Compute base name (filename without directory).
    # We use a UUID to avoid clashes with existing files,
    # and ensure that the name is compatible with the filesystem.
    # Save to disk
    if operation == 'create':
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        if fileobj.filename == '':
            flask.abort(400)
        connection.execute(
            "INSERT OR REPLACE INTO posts( filename , owner) VALUES (?, ?)",
            (uuid_basename, logname, )
        )
        if 'target' not in flask.request.args.to_dict():
            return flask.redirect('/users/' + logname + '/')
        return flask.redirect(flask.request.args.to_dict()['target'])
    if operation == 'unlike':
        connection.execute(
            "DELETE FROM likes WHERE postid = ?",
            (flask.request.form.get('post'), )
        )
    if operation == "like":
        connection.execute(
            "INSERT INTO likes(owner, postid ) VALUES (?, ?)",
            (logname, flask.request.form.get('postid'), )
        )

    if operation == 'delete':
        cur = connection.execute(
            "SELECT owner, postid FROM posts WHERE postid =?",
            (flask.request.form.get('postid'), )
        )
        poster = cur.fetchall()[0]
        if poster['owner'] != logname:
            flask.abort(403)
        cur2 = connection.execute(
            "SELECT filename FROM posts WHERE postid = ?",
            (flask.request.form.get('postid'), )
        )
        filename = cur2.fetchall()
        connection.execute(
            "DELETE FROM posts WHERE filename = ?",
            (filename[0]["filename"], )
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/filename[0]['filename']
        os.remove(path)
    # print("post posts: ",flask.request.args.to_dict()['target'])
    if 'target' not in flask.request.args.to_dict():
        return flask.redirect('/users/' + logname + '/')
    return flask.redirect(flask.request.args.to_dict()['target'])
