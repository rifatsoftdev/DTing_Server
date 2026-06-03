import json
import firebase_admin
from firebase_admin import credentials

from app.constants import ENV




service_account_info = json.loads(ENV.FIREBASE_SERVICE_ACCOUNT)
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)



