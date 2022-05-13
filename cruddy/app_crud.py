"""control dependencies to support CRUD app routes and APIs"""
from flask import Blueprint, render_template, request, url_for, redirect, jsonify, make_response, abort
from flask_login import login_required

from cruddy.query import *

# blueprint defaults https://flask.palletsprojects.com/en/2.0.x/api/#blueprint-objects
app_crud = Blueprint('crud', __name__,
                     url_prefix='/',
                     template_folder='templates/cruddy/',
                     static_folder='static',
                     static_url_path='static')

""" Blueprint is established to isolate Application control code for CRUD operations, key features:
    1.) 'Users' table control methods, controls relationship between User Actions and Database Model
    2.) Control methods are achieved using app routes for each CRUD operations
    3.) login required to restrict CRUD operations to identified users
"""


def admin():
    try:
        if current_user.privilege == 0:
            return 0
        elif current_user.privilege == 1:
            return 1
        else:
            return 2
    except AttributeError:
        abort(404)


@app_crud.route('/crud')
def crud():
    p = admin()
    if p == 0:
        return render_template("crud.html", table=users_all(), user=current_user)
    elif p == 1:
        return render_template("readcrud.html", table=users_all(), user=current_user)
    else:
        abort(404)


@app_crud.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app_crud.route('/logou')
@login_required
def logou():
    return render_template("logout.html", logout=logout_user())


# Flask-Login directs unauthorised users to this unauthorized_handler
@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    return redirect(url_for('crud.crud_login'))


# if login url, show phones table only
@app_crud.route('/login/', methods=["GET", "POST"])
def crud_login():
    # obtains form inputs and fulfills login requirements
    if request.form:
        email = request.form.get("email")
        password = request.form.get("password")
        if login(email, password):       # zero index [0] used as email is a tuple
            return redirect(url_for('crud.crud'))

    # if not logged in, show the login page
    return render_template("login.html")


@app_crud.route('/authorize/', methods=["GET", "POST"])
def crud_authorize():
    # check form inputs and creates user
    if request.form:
        # validation should be in HTML
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password1 = request.form.get("password1")
        password2 = request.form.get("password1")
        # if password1 != password2:
        #
        if authorize(user_name, email, password1, phone, 2):    # zero index [0] used as user_name and email are type tuple
            return redirect(url_for('crud.crud_login'))
    # show the auth user page if the above fails for some reason
    return render_template("authorize.html")


# CRUD create/add
@app_crud.route('/create/', methods=["POST"])
def create():
    """gets data from form and add it to Users table"""
    if request.form:
        po = Users(
            request.form.get("name"),
            request.form.get("email"),
            request.form.get("password"),
            request.form.get("phone"),
            2
        )
        po.create()
    return redirect(url_for('crud.crud'))


# CRUD read
@app_crud.route('/read/', methods=["POST"])
def read():
    """gets userid from form and obtains corresponding data from Users table"""
    table = []
    if request.form:
        userid = request.form.get("userid")
        po = user_by_id(userid)
        if po is not None:
            table = [po.read()]  # placed in list for easier/consistent use within HTML
    return render_template("crud.html", table=table)


# CRUD update
@app_crud.route('/update/', methods=["POST"])
def update():
    """gets userid and name from form and filters and then data in  Users table"""
    if request.form:
        userid = request.form.get("userid")
        name = request.form.get("name")
        po = user_by_id(userid)
        if po is not None:
            po.update(name)
    return redirect(url_for('crud.crud'))


# CRUD delete
@app_crud.route('/delete/', methods=["POST"])
def delete():
    """gets userid from form delete corresponding record from Users table"""
    if request.form:
        userid = request.form.get("userid")
        po = user_by_id(userid)
        if po is not None:
            po.delete()
    return redirect(url_for('crud.crud'))


# Search Form
@app_crud.route('/search/')
def search():
    """loads form to search Users data"""
    return render_template("search.html")


# Search request and response
@app_crud.route('/search/term/', methods=["POST"])
def search_term():
    """ obtain term/search request """
    req = request.get_json()
    term = req['term']
    response = make_response(jsonify(users_ilike(term)), 200)
    return response