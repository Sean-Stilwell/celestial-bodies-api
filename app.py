import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from flask import Flask, jsonify, Blueprint
from flask_restx import Api, Resource, fields

KEY_VAULT_URL = "https://fsdh-proj-dw1-poc-kv.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

# Retrieve the secrets containing DB connection details
DB_NAME = "fsdh"
try:
    DB_HOST = secret_client.get_secret("datahub-psql-server").value
    DB_USER = secret_client.get_secret("datahub-psql-admin").value
    DB_PASS = secret_client.get_secret("datahub-psql-password").value
except Exception as e:
    DB_HOST = "localhost"
    DB_USER = "postgres"
    DB_PASS = "password"

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/webapp-AHT')
api = Api(blueprint, version='1.0', title='Sample FSDH API | Exemple d\'API DHSF',
          description='A simple API for accessing and using storage and database on the FSDH | Une API simple pour accéder et utiliser le stockage et la base de données sur le DHSF', doc='/')

ns = api.namespace('api', description='Example methods for accessing FSDH data | Méthodes d\'exemple pour accéder aux données du DHSF')

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
    '''Connect to the PostgreSQL database | Se connecter à la base de données PostgreSQL'''
    conn = psycopg2.connect(
        host = DB_HOST,
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASS
    )
    return conn

@ns.route('/')
class CelestialBodyList(Resource):
    @ns.doc('read_celestial_bodies')
    def get(self):
        return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
