import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Person, Image


PERSONS_PER_PAGE = 10

# paginate each pages to render 10 person on each page
# From the PERSONS_PER_PAGE constant


def person_paginated(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * PERSONS_PER_PAGE
    end = start + PERSONS_PER_PAGE

    persons = [person.format() for person in selection]
    current_person = persons[start:end]

    return current_person
# organize each images to match 'id': 'type'


def converted_images():
    images = Image.query.order_by(Image.id).all()
    dict = {}
    for image in images:
        dict[image.id] = image.link
    return dict


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # set up CORS, allowing all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE,PUT,OPTIONS')
        return response
    @app.route('/')
    def index():
        return 'Welcome to people api by kelani. fetch people: https://apipeoplekelani.herokuapp.com/persons; fetch images: https://apipeoplekelani.herokuapp.com/images; fetch specific images from people: https://apipeoplekelani.herokuapp.com/images/2/persons'
    @app.route('/images')
    def get_images():
        ''' Render the data for all images'''
        images = converted_images()

        if len(images) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'images': images,
            "total_images": len(Image.query.all()),
        })

    @app.route('/persons')
    def get_persons():
        ''' Render persons based on each images'''
        selection = Person.query.order_by(Person.id).all()
        total_persons = len(selection)
        current_persons = person_paginated(request, selection)
        images = converted_images()

        if len(current_persons) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'persons': current_persons,
            'total_persons': total_persons
        })

    @app.route('/persons/<int:person_id>', methods=['DELETE'])
    def delete_person(person_id):
        ''' Renders Delete for a particular person'''
        try:
            person = Person.query.filter(
                Person.id == person_id).one_or_none()

            if person is None:
                abort(404)

            person.delete()
            selection = Person.query.order_by(Person.id).all()
            current_person = person_paginated(request, selection)

            return jsonify(
                {
                    'success': 'Deleted',
                    'deleted': person_id,
                    'person': current_person,
                    'total_person': len(Person.query.all())}
            )
        except:
            abort(422)

    @app.route('/persons', methods=['POST'])
    def create_person():
        ''' Renders avalability to create new persons'''
        body = request.get_json()

        image = body.get('image')
        new_f_name = body.get('f_name')
        new_age = body.get('age')
        new_l_name = body.get('l_name')
        if new_l_name is None or new_f_name is None or image is None or new_age is None:
            abort(422)
        searchTerm = body.get('searchTerm')

        try:
            if searchTerm:
                selection = Person.query.filter(
                    Person.person.ilike(f'%{searchTerm}%')).all()

                if len(selection) == 0:
                    abort(404)

                current_persons = person_paginated(request, selection)

                return jsonify({
                    'success': True,
                    'persons': current_persons,
                    'total_persons': len(Person.query.all())
                })
            else:           
                person = person(
                    image=image,
                    f_name=new_f_name,
                    l_name=new_l_name,
                    age=new_age)
                person.insert()

                selection = person.query.order_by(person.id).all()
                if new_l_name is None or new_f_name is None or image is None or new_age is None:
                    abort(422)
                current_person = person_paginated(request, selection)

                return jsonify(
                    {
                        'success': True,
                        'created': person.id,
                        'person_created': person.person,
                        'person': current_person,
                        'total_persons': len(Person.query.all()),
                    }
                )
        except:
            abort(422)

    @app.route('/images/<int:Image_id>/persons')
    def image(Image_id):
        ''' Renders all persons for a particular image'''

        image = Image.query.filter(
            Image_id == Image.id).one_or_none()
        if image is None:
            abort(404)

        selection = Person.query.filter(
            Person.image == image.link).all()
        current_persons = person_paginated(request, selection)

        return jsonify({
            'success': True,
            'persons': current_persons,
            'total_persons': len(Person.query.all()),
            'image': image.link
        })

    # Error handllerss for each error that may occur
    @app.errorhandler(404)
    def handle_not_found_error404(e):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def handle_bad_request_error400(e):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def handle_unprocessable_error422(e):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
