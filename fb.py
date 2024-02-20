import firebase_admin
from firebase_admin import credentials, auth, db
from fb_config import CREDENTIAL_PATH, DB_URL
from fastapi import Request, HTTPException

from models import Employee

cred = credentials.Certificate(CREDENTIAL_PATH)
app = firebase_admin.initialize_app(cred, {
    'databaseUrl': DB_URL
})

ref = db.reference('/user', app, DB_URL)


def get_firebase_user(request: Request):
    """Get the user details from Firebase, based on TokenID in the request

    :param request: The HTTP request
    """

    id_token = request.headers.get('Authorization')
    if not id_token:
        raise HTTPException(status_code=400, detail='TokenID must be provided')

    try:
        claims = auth.verify_id_token(id_token)
        print(claims)
        return claims
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail='Unauthorized')


def save_intranet_user(input: list[Employee]):
    if not input:
        return

    for x in input:
        # Use the 'idx' field as a key to directly reference the employee record
        employee_ref = ref.child(str(x.idx))

        # Update the record with the new data
        employee_ref.update(x.toJSON())


def get_intranet_user(index: int = -1):
    if index == -1:
        # Get user list
        return list(ref.get().values())
    else:
        # Get single user
        return ref.child(str(index)).get()
