import psycopg2
import os
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='Sample FSDH API | Exemple d\'API DHSF',
          description='A simple API for accessing and using storage and database on the FSDH | Une API simple pour accéder et utiliser le stockage et la base de données sur le DHSF')

ns = api.namespace('fsdh-dhsf', description='Example methods for accessing FSDH data | Méthodes d\'exemple pour accéder aux données du DHSF')

# Model definition for expected data
celestial_body_model = api.model('CelestialBody', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a celestial body | L\'identifiant unique d\'un corps céleste'),
    'name': fields.String(required=True, description='The name of the celestial body | Le nom du corps céleste'),
    'body_type': fields.String(description='The type of celestial body | Le type de corps céleste'),
    'mean_radius_km': fields.Float(description='The mean radius of the celestial body | Le rayon moyen du corps céleste'),
    'mass_kg': fields.Float(description='The mass of the celestial body | La masse du corps céleste'),
    'distance_from_sun_km': fields.Float(description='The distance of the celestial body from the sun | La distance du corps céleste au soleil')
})

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

@ns.route('/celestial_bodies_db/')
class CelestialBodyList(Resource):
    @ns.doc('read_celestial_bodies')
    def get(self):
        '''Read all celestial bodies from the database | Lire tous les corps célestes de la base de données'''
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM celestial_bodies;')
        celestial_bodies = cur.fetchall()
        cur.close()
        conn.close()

        # Convert Decimal to float for JSON serialization
        bodies_list = [
            {
                'id': body[0],
                'name': body[1],
                'body_type': body[2],
                'mean_radius_km': float(body[3]) if body[3] is not None else None,
                'mass_kg': float(body[4]) if body[4] is not None else None,
                'distance_from_sun_km': float(body[5]) if body[5] is not None else None,
            }
            for body in celestial_bodies
        ]
        
        return jsonify({'celestial_bodies': bodies_list})

    @ns.doc('create_celestial_body')
    @ns.expect(celestial_body_model)  # This uses your defined model for validation
    @ns.response(201, 'Celestial body created successfully | Corps céleste créé avec succès')
    def post(self):
        '''Create a new celestial body | Créer un nouveau corps céleste'''
        data = api.payload  # This contains the data sent by the client
        conn = get_db_connection()
        cur = conn.cursor()
        #query = f"INSERT INTO celestial_bodies (name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) VALUES ('{data['name']}', '{data['body_type']}', {data['mean_radius']}, {data['mass']}, {data['distance_from_sun']})"
        cur.execute('INSERT INTO celestial_bodies (name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) VALUES (%s, %s, %s, %s, %s)', (data['name'], data['body_type'], data['mean_radius_km'], data['mass_kg'], data['distance_from_sun_km']))
        conn.commit()
        return {"message": "Celestial body created successfully | Corps céleste créé avec succès"}, 201
    
    @ns.doc('update_celestial_body')
    @ns.expect(celestial_body_model)
    @ns.response(404, 'Celestial body not found | Corps céleste non trouvé')
    @ns.response(200, 'Celestial body updated successfully | Corps céleste mis à jour avec succès')
    def put(self):
        '''Update a celestial body by its ID | Mettre à jour un corps céleste par son ID'''
        data = api.payload  # This contains the data sent by the client
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM celestial_bodies WHERE id = %s', (data['id'],))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return {"message": "Celestial body not found | Corps céleste non trouvé"}, 404
        
        cur.execute('UPDATE celestial_bodies SET name = %s, body_type = %s, mean_radius_km = %s, mass_kg = %s, distance_from_sun_km = %s WHERE id = %s', (data['name'], data['body_type'], data['mean_radius_km'], data['mass_kg'], data['distance_from_sun_km'], data['id']))
        conn.commit()
        cur.close()
        conn.close()
        return {'message': 'Celestial body updated successfully | Corps céleste mis à jour avec succès'}, 200
    
    @ns.doc('delete_celestial_body')
    @ns.expect(celestial_body_model)
    @ns.response(404, 'Celestial body not found | Corps céleste non trouvé')
    @ns.response(200, 'Celestial body deleted successfully | Corps céleste supprimé avec succès')
    def delete(self):
        '''Delete a celestial body by its ID | Supprimer un corps céleste par son ID'''
        data = api.payload  # This contains the data sent by the client
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM celestial_bodies WHERE id = %s', (data['id'],))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return {"message": "Celestial body not found | Corps céleste non trouvé"}, 404

        cur.execute('DELETE FROM celestial_bodies WHERE id = %s', (data['id'],))
        conn.commit()
        cur.close()
        conn.close()
        return {'message': 'Celestial body deleted successfully | Corps céleste mis à jour avec succès'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
