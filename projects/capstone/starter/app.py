import os
import json
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf import Form
from auth.auth import AuthError, requires_auth
from werkzeug.exceptions import HTTPException
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from models import *
from forms import *


def create_app(test_config=None):

    app = Flask(__name__)
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    setup_db(app)
    migrate = Migrate(app, db)
    CORS(app)
    oauth = OAuth(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
        return response

    auth0 = oauth.register(
        'auth0',
        client_id='zNzK3s62YQ9xAx0RqkTfOWm7NN5U7SCe',
        client_secret='1EUaLZASC5yhg5mBABU19WeLwgEXtMt1CMNTHNd6dqbktVjHduPy5mpNXGVT4HQq',
        api_base_url='https://capstone-projects.auth0.com',
        access_token_url='https://capstone-projects.auth0.com/oauth/token',
        authorize_url='https://capstone-projects.auth0.com/authorize',
        client_kwargs={
            'scope': 'openid profile email',
            },
    )


    '''
     Endpoints for login 
    '''
    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')


    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
            }
        return redirect('/')


    '''
     Endpoints for home page 
    '''
    @app.route('/')
    def index():
        return render_template('home.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))


    '''
     Endpoints for actors 
    '''
    # gets all actors and posts a new actor
    @app.route('/actors', methods=["GET"])
    @requires_auth('get:actors')
    def actors(token):
        return render_template('pages/actors.html', actors=Actor.query.all())

    @app.route('/actors', methods=["POST"])
    @requires_auth('post:actors')
    def post_actor(token):
        try:
            name = request.form.get("name")
            age = request.form.get("age")
            gender = request.form.get("gender")
            new_actor = Actor(name=name, age=age, gender=gender)
            new_actor.insert()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            return render_template('pages/actors.html')

    # gets the form for posting a new actor profile:
    @app.route('/actors/create', methods=["GET"])
    @requires_auth('post:actors')
    def create_actor(token):
        form = ActorForm()
        return render_template('forms/post_actor.html', form=form)

    # gets an actor's profile
    @app.route('/actors/<int:id>', methods=["GET"])
    @requires_auth('get:actors')
    def show_actor(token, id):
        actor = Actor.query.filter_by(id=id).first()
        return render_template('pages/actor_profile.html', actor=actor)

    # edits existing actor:
    @app.route('/actors/<int:id>/edit', methods=["POST"])
    @requires_auth('patch:actor')
    def edit_actor(token, id):
        try:
            actor = Actor.query.filter_by(id=id).first()
            new_name = request.form.get("name", None)
            new_age = request.form.get("age", None)
            new_gender = request.form.get("gender", None)

            if new_name:
                actor.name = new_name
            if new_age:
                actor.age = new_age
            if new_gender:
                actor.gender = new_gender

            actor.update()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            return redirect(url_for('actors'))

    # deletes actor
    @app.route('/actors/<int:id>', methods=["DELETE"])
    @requires_auth('delete:actor')
    def delete_actor(token, id):
        try:
            actor = Actor.query.filter(Actor.id == id).one_or_none()
            if actor is None:
                return jsonify({
                    "message": "actor not found"
                    })
            actor.delete()
        except:
            db.session.rollback()
            return jsonify({
                "message": "there was an error deleting"
                })
        finally:
            db.session.close()
            return redirect(url_for('actors'))


    # gets the form for editing an actor profile
    @app.route('/actors/<int:id>/edit', methods=["GET"])
    def get_edit_actor(id):
        actor = Actor.query.filter_by(id=id).one()
        form = ActorForm()
        return render_template('forms/edit_actor.html', actor=actor, form=form)


#----------------------------------------------------------------------------#
# Movies Endpoints
#----------------------------------------------------------------------------#
    # get all movies and post a new movie
    @app.route('/movies', methods=["GET"])
    @requires_auth('get:movies')
    def movies(token):
        return render_template('pages/movies.html', movies=Movie.query.order_by(Movie.id).all())


    @app.route('/movies', methods=["POST"])
    @requires_auth('post:movies')
    def create_movie(token):
        try:
            title = request.form.get("title")
            release_date = request.form.get("release_date")
            new_movie = Movie(title=title, release_date=release_date)
            new_movie.insert()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            return redirect(url_for('movies'))


    # delete a movie
    @app.route('/movies/<int:id>/delete', methods=["DELETE"])
    @requires_auth('delete:movie')
    def delete_movie(token, id):
        try:
            movie = Movie.query.filter(Movie.id == id).one_or_none()

            if movie is None:
                return jsonify({
                    "message": "movie not found"
                    })

            movie.delete()
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({
                "message": "there was an error deleting"
                })
        finally:
            db.session.close()
            return redirect(url_for('movies'))


    @app.route('/movies/<int:id>/update', methods=["POST"])
    @requires_auth('patch:movie')
    def update_movie(token, id):
        try:
            movie = Movie.query.filter_by(id=id).one_or_none()
            new_title = request.args.get("title",None)
            new_release_date = request.args.get("release_date",None)

            if new_title:
                movie.title = new_title
            if new_release_date:
                movie.release_date = new_release_date

            movie.update()
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            return redirect(url_for('movies'))


    @app.route('/movies/create')
    def get_movie_create():
        form = MovieForm()
        return render_template('forms/post_movie.html', form=form)

    @app.route('/movies/<int:id>', methods=["GET"])
    def get_movie_profile(id):
        movie = Movie.query.filter_by(id=id).first()
        return render_template('pages/movie_profile.html', movie=movie)

    @app.route('/movies/<int:id>/edit')
    def get_edit_movie(id):
        movie = Movie.query.filter_by(id=id).first()
        form = MovieForm()
        return render_template('pages/edit_movie.html', movie=movie, form=form)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)