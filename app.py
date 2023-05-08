import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)
# Get the value of the secret key from the environment
secret_key = os.environ.get("SECRET_KEY")

# Check if the secret key is set
if secret_key is None:
    print("Error: SECRET_KEY environment variable is not set.")
else:
    # Print the value of the secret key in the log
    print(f"Secret key is: {secret_key}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload():
    # Get user inputs
    access_token = request.form.get("access_token")
    file = request.files["file"]
    is_public = True if request.form.get("public") == "on" else False
    description = request.form.get("description")

    # Set headers
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Read the uploaded file
    file_content = file.read()

    # Create a new Gist
    payload = {
        "description": description,
        "public": is_public,
        "files": {
            file.filename: {
                "content": file_content.decode("utf-8")
            }
        }
    }
    response = requests.post("https://api.github.com/gists", headers=headers, json=payload)

    if response.status_code == 201:
        # Gist created successfully
        gist_id = response.json()["id"]
        gist_url = response.json()["html_url"]
        raw_url = response.json()["files"][file.filename]["raw_url"]
        return render_template("success.html", gist_url=gist_url, raw_url=raw_url)
    else:
        # Gist creation failed
        error_message = response.json()["message"]
        return render_template("error.html", error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)
