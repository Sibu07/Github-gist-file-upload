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

# Define allowed extensions
allowed_extensions = {"txt", "md", "py", "rb", "js", "java", "c", "cpp", "h", "hpp", "css", "html", "xml", "json", "yml", "yaml", "ini", "sh", "ps1", "bat",  "php", "asp", "aspx", "jsp", "pl", "cgi", "sql", "swift", "kt", "scala", "groovy", "go", "dart", "lua", "r", "m", "matlab", "asm", "coffee", "jsx", "tsx", "vue", "ts", "scss", "sass", "less", "styl", "rs", "perl", "jl", "cobol", "fortran", "f90", "f95", "f03", "f08", "v", "vhdl", "verilog", "dart", "hs", "lhs", "elm", "idr", "agda", "lean", "ml", "mli", "sml", "sig", "fun", "d", "adb", "ada", "nim", "nimble", "rkt", "scheme", "clj", "cljs", "cljc", "edn", "factor", "fancy", "forth", "fsl", "haxe", "io", "jl", "k", "ls", "forth", "frt", "fs", "purs", "re", "rlib", "rlibc", "sc", "sq", "sas", "sce", "sci", "tcl", "zsh", "fish", "awk", "sed", "lua", "moon", "svelte", "gitconfig"}

# Define not allowed extensions
notallowed_extensions = {"jpg", "jpeg", "png", "gif", "svg", "bmp", "tiff", "avi", "mp4", "mov", "wmv", "flv", "mkv", "webm", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "mp3", "aac", "wav", "wma", "midi", "m4a", "ogg", "flac", "alac", "opus", "weba", "avi", "wmv", "m4v", "f4v", "f4p", "f4a", "f4b", "3gp", "3g2", "m2v", "mpg", "mpeg", "mpv", "pdf", "ps", "eps", "indd", "ai", "tif", "tiff", "ico", "icns", "jpeg2000", "jp2", "jpx", "xbm", "webp", "raw", "arw", "cr2", "nef", "nrw", "rw2", "rwl", "sr2"}


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
        # Check if file was selected
    if not file:
        error_message = "No file selected. Please select a file to upload."
        return render_template("error.html", error_message=error_message)


    # Check if file has an allowed extension
    file_extension = file.filename.rsplit(".", 1)[1].lower()

    # Check if file is not allowed extension
    if file_extension in notallowed_extensions:
        error_message = f"File extension '{file_extension}' is not allowed \n\nDon't use this extensions: {', '.join(notallowed_extensions)}."
        return render_template("error.html", error_message=error_message)

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

    # Send a test request to GitHub to check if the PAT is valid
    test_request = requests.get("https://api.github.com/user", headers=headers)

    if test_request.status_code == 401:
        # Invalid token
        error_message = "Invalid or missing GitHub access token. Please create a new Personal Access Token (PAT) with the 'gist' scope and try again."
        return render_template("error.html", error_message=error_message)

    # The token is valid. Proceed with creating the Gist
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
