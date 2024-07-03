from requests_oauth2client import OAuth2Client
import osmapi
from django.conf import settings


client_id = settings.OPEN_STREET_MAPS_CLIENT_ID
client_secret = settings.OPEN_STREET_MAPS_CLIENT_SECRET

# special value for redirect_uri for non-web applications
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

authorization_base_url = "https://master.apis.dev.openstreetmap.org/oauth2/authorize"
token_url = "https://master.apis.dev.openstreetmap.org/oauth2/token"

oauth2client = OAuth2Client(
    token_endpoint=token_url,
    authorization_endpoint=authorization_base_url,
    redirect_uri=redirect_uri,
    auth=(client_id, client_secret),
    code_challenge_method=None,
)

api = osmapi.OsmApi(api="https://api06.dev.openstreetmap.org")