import random
import json
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, Response
import os

def generate_roll_no():
    prefixes = [
        "CSB23", "ECB23", "MEB23", "CEB23", "FEB23", "EEB23",
        "CSB24", "ECB24", "MEB24", "CEB24", "FEB24", "EEB24",
        "DBD24","SOM24","EGI23","EGI24"
    ]

    prefix = random.choice(prefixes)
    roll = random.randint(1, 83)

    return f"{prefix}{roll:03d}"

def photo(session_id):
    r = requests.get(
        "http://agnee.tezu.ernet.in:8999/cgi-bin/koha/opac-patron-image.pl",
        cookies={"CGISESSID": session_id},
        stream=True
    )

    return Response(
        r.content,
        content_type=r.headers.get("Content-Type", "image/jpeg")
    )

def fetch_profile(session_id):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    profile_url = "http://agnee.tezu.ernet.in:8999/cgi-bin/koha/opac-memberentry.pl"

    try:
        response = session.get(
            profile_url,
            headers=headers,
            cookies={"CGISESSID": session_id},
            timeout=10
        )

        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "roll_no": None,
            "name": None,
            "primary_phone": None,
            "picture_url": f'/photo/{session_id}'
            }

        # Name
        user_label = soup.select_one(".userlabel")
        if user_label:
            text = user_label.get_text(" ", strip=True)
            text = re.sub(r"^Welcome,\s*", "", text)
            result["name"] = text

        # Roll No
        card_label = soup.find(
            "label",
            string=lambda x: x and "Library card number" in x
        )

        if card_label:
            parent = card_label.parent
            text = parent.get_text(" ", strip=True)

            match = re.search(r'([A-Z]{3}\d{5})', text)
            if match:
                result["roll_no"] = match.group(1)

        # Primary Phone
        phone_input = soup.find("input", {"id": "borrower_phone"})
        if phone_input:
            result["primary_phone"] = phone_input.get("value")

        # Only return if something was found
        if any([
            result["roll_no"],
            result["name"],
            result["primary_phone"]
        ]):
            return result

        return None

    except Exception as e:
        print("Error:", e)
        return None

def login(username):
    url = "http://agnee.tezu.ernet.in:8999/cgi-bin/koha/opac-user.pl"

    # Matching your exact request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "http://agnee.tezu.ernet.in:8999",
        "Connection": "keep-alive",
        "Referer": "http://agnee.tezu.ernet.in:8999/cgi-bin/koha/opac-main.pl?logout.x=1",
        "Upgrade-Insecure-Requests": "1",
        "Priority": "u=0, i"
    }

    data = {
        "koha_login_context": "opac",
        "userid": username,
        "password": "xyz"
    }

    # requests automatically sets Content-Type to application/x-www-form-urlencoded
    # and calculates Content-Length when using the `data` parameter.
    response = requests.post(
        url,
        headers=headers,
        data=data,
        allow_redirects=False
    )
    return response

def getProfileDetails():
    roll_no = generate_roll_no()
    auth_detils = login(roll_no)
    session_id = auth_detils.cookies.get("CGISESSID")
    profile = fetch_profile(session_id)
    if profile.get("roll_no") is None:
        return getProfileDetails()
    else:
        return profile

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/profile")
def profile():
    profile = getProfileDetails()
    if profile:
        return(json.dumps(profile, indent=2))
    else:
        return("null")

@app.route("/photo/<session_id>")
def photo(session_id):
    r = requests.get(
        "http://agnee.tezu.ernet.in:8999/cgi-bin/koha/opac-patron-image.pl",
        cookies={"CGISESSID": session_id},
        stream=True
    )

    return Response(
        r.content,
        content_type=r.headers.get("Content-Type", "image/jpeg")
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )
