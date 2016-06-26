import getpass
from six.moves import input

from . import Sense


def login(sense):
    username = input("Sense email: ")
    password = getpass.getpass("Sense password: ")

    print("Attempting to log into Sense's API")
    sense.login(username=username, password=password)

def test(sense):
    print("\n".join((x['message'] for x in sense.room_current(temp_unit="f").values())))

if __name__ == "__main__":
    client_id = input("Sense OAuth Client ID: ")
    client_secret = input("Sense OAuth Client Secret: ")
    sense = Sense(client_id=client_id, client_secret=client_secret)

    login(sense)
    print("Success!")

    print("Attempting to query the Sense API")
    test(sense)
    print("Success!")
