import psycopg2
import os
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='Celestial Body API',
          description='A simple API for managing celestial bodies')

ns = api.namespace('celestial_bodies', description='Celestial bodies operations')

# Model definition for expected data
celestial_body_model = api.model('CelestialBody', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a celestial body'),
    'name': fields.String(required=True, description='The name of the celestial body'),
    'body_type': fields.String(description='The type of celestial body'),
    'mean_radius_km': fields.Float(description='The mean radius of the celestial body'),
    'mass_kg': fields.Float(description='The mass of the celestial body'),
    'distance_from_sun_km': fields.Float(description='The distance of the celestial body from the sun')
})

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

@ns.route('/')
class CelestialBodyList(Resource):
    @ns.doc('list_celestial_bodies')
    def get(self):
        '''List all celestial bodies'''
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
    @ns.response(201, 'Celestial body created successfully')
    def post(self):
        '''Create a new celestial body'''
        data = api.payload  # This contains the data sent by the client
        conn = get_db_connection()
        cur = conn.cursor()
        #query = f"INSERT INTO celestial_bodies (name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) VALUES ('{data['name']}', '{data['body_type']}', {data['mean_radius']}, {data['mass']}, {data['distance_from_sun']})"
        cur.execute('INSERT INTO celestial_bodies (name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) VALUES (%s, %s, %s, %s, %s)', (data['name'], data['body_type'], data['mean_radius_km'], data['mass_kg'], data['distance_from_sun_km']))
        conn.commit()
        return {"message": "Celestial body created successfully"}, 201
    
    @ns.doc('delete_celestial_body')
    @ns.expect(celestial_body_model)
    @ns.response(404, 'Celestial body not found')
    @ns.response(200, 'Celestial body deleted successfully')
    def delete(self):
        '''Delete a celestial body by its ID'''
        data = api.payload  # This contains the data sent by the client
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM celestial_bodies WHERE id = %s', (data['id'],))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return {"message": "Celestial body not found"}, 404

        cur.execute('DELETE FROM celestial_bodies WHERE id = %s', (data['id'],))
        conn.commit()
        cur.close()
        conn.close()
        return {'message': 'Celestial body deleted successfully'}, 200

if __name__ == '__main__':
    app.run(debug=True)
