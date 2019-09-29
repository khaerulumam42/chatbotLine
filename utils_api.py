import requests

def register_user(username, email, password, phone):
    data = {"name":username, "email":email, "password":password, "phone_no":phone}
    reg = requests.post('http://18.223.160.194/Laundry/api/ebregister', files=data)
    return reg.json()

def login_user(email, password):
    data = {"email":email, "password":password}
    login = requests.post('http://18.223.160.194/Laundry/api/eblogin', files=data)
    return login.json()