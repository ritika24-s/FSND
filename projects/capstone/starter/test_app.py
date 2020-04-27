import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime, time as time_

from app import create_app
from models import *


class AgencyTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)

        self.new_project = {
            'title': 'Lucy',
            'release_date': '10/04/2014'
        }

        self.new_actor = {
            'name': 'Angela Jolie',
            'age': '47',
            'gender': 'Female'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass

    def testIndex(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

    def testActors(self):
        res = self.client().get('/actors')
        self.assertEqual(res.status_code, 200)

    def testActorsFail(self):
        res = self.client().get('/actrs')
        self.assertEqual(res.status_code, 404)

    def testMovies(self):
        res = self.client().get('/movies')
        self.assertEqual(res.status_code, 200)

    def testMoviesFail(self):
        res = self.client().get('move')
        self.assertEqual(res.status_code, 404)

    def testCreateNewActor(self):
        res = self.client().post('/actors', json=self.new_actor)
        self.assertEqual(res.status_code, 200)

    def testCreateNewActorFail(self):
        res = self.client().post('/actor', json=self.new_actor)
        self.assertEqual(res.status_code, 404)

    def testCreateNewMovie(self):
        res = self.client().post('/movies', json=self.new_movie)
        self.assertEqual(res.status_code, 200)

    def testCreateNewMovieFail(self):
        res = self.client().post('/movie', json=self.new_movie)
        self.assertEqual(res.status_code, 404)

    def testPatchActor(self):
        res = self.client().post('/actor/1/edit', json=self.new_actor)
        self.assertEqual(res.status_code, 200)

    def testPatchActorFail(self):
        res = self.client().post('/actors/1/edit', json=self.new_actor)
        self.assertEqual(res.status_code, 404)

    def testDeleteActor(self):
        res = self.client().post('/actors/1')
        self.assertEqual(res.status_code, 200)

    def testDeleteMovie(self):
        res = self.client().post('/movies/1/delete')
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()