#!/usr/bin/python3

from stem.control import Controller

import http.server
import os
import subprocess

def main():
    controller = Controller.from_port()
    controller.authenticate()
    response = controller.create_ephemeral_hidden_service({80: 8080}, await_publication=True)

    onion_url = "http://" + response.service_id + ".onion"
    print(onion_url)

    os.chdir("tricksterblog/")

    subprocess.run(["hugo", "--baseURL", onion_url])

    os.chdir("public/")

    subprocess.run(["python3", "-m", "http.server", "8080"])


if __name__ == "__main__":
    main()

