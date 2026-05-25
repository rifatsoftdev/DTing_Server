import requests


def post_request(url, payload):
    response = requests.post(url, json=payload)
    return response.json()

def get_request(url):
    response = requests.get(url)
    return response.json()



registration_payload = {
    "full_name": "David",
    "email_address": "rmdrifat547@gmail.com",
    "phone_number": "01812345673",
    "country_code": "+88",
    "user_password": "1s22s22p6",
    
    "device_id": "device_id",
    "device_uuid": "device_uuid"
}

login_payload = {
    "email_address": "rmdrifat5471@gmail.com",
    "phone_number": "null",
    "country_code": "null",
    "user_password": "1s22s22p6",
    "device_id": "device_id",
    "device_uuid": "device_uuid"
}

if __name__ == "__main__":
    # Example usage
    url = "http://192.168.1.100:8000/"


    response = post_request(f"{url}/auth/register", registration_payload)
    print(response)

    # response = post_request(f"{url}/auth/login", login_payload)
    # print(response)