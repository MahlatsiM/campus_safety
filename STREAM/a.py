# create_user.py
from auth import add_user

username = "mahlatsi"
email = "mahlatsimm1510@gmail.com"
first_name = "Mahlatsi"
last_name = "Mashilo"
password = "Mahla#03"  # pick a secure password


user_id = add_user(username, email, first_name, last_name, password)
print(f"User created with ID: {user_id}")
