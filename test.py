import requests

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


def main():
    # Attempting login
    response = login("CSB23079")

    print(f"Status Code: {response.status_code}")

    # Extracting the CGISESSID cookie
    cgisessid = response.cookies.get("CGISESSID")

    if cgisessid:
        print(f"Successfully grabbed CGISESSID: {cgisessid}")
    else:
        print("CGISESSID cookie not found in the response.")
        # Debugging fallback: check raw Set-Cookie headers if needed
        print("Cookies received:", response.cookies.get_dict())

if __name__ == "__main__":
    main()
