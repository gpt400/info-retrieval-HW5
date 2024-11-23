from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs, urlparse
from query_processor import QueryProcessor
import json

# file paths
DICT_PATH = os.path.join("output", "dict")
POST_PATH = os.path.join("output", "post")
MAP_PATH = os.path.join("output", "map")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    processor = QueryProcessor(DICT_PATH, POST_PATH, MAP_PATH)
except FileNotFoundError as e:
    print(f"Error initializing QueryProcessor: {e}")
    processor = None

# handle GET requests
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/query":
            self.handle_query(parsed_url.query)
        elif parsed_url.path.startswith("/wizard.png"):
            self.serve_root_file("wizard.png")
        elif parsed_url.path.startswith("/files/"):
            self.serve_file(parsed_url.path)
        else:
            self.serve_frontend()

# serve file from root
    def serve_root_file(self, file_name):
        file_path = os.path.join(ROOT_DIR, file_name)
        if os.path.isfile(file_path):
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found.")

# serve files from corpus/files dir
    def serve_file(self, file_path):
        files_dir = os.path.join(ROOT_DIR, "corpus", "files")
        local_path = os.path.join(files_dir, file_path.lstrip("/files/"))
        if os.path.isfile(local_path):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open(local_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found.")

# serve user front end
    def serve_frontend(self, results=None, query=""):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>The Oracle</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 2em;
                }}
                .query-box {{
                    margin: 1em auto;
                    max-width: 600px;
                }}
                input[type="text"] {{
                    width: 80%;
                    padding: 0.5em;
                    font-size: 1em;
                }}
                button {{
                    padding: 0.5em;
                    font-size: 1em;
                }}
                .results {{
                    margin-top: 2em;
                    text-align: left;
                    max-width: 800px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .result-item {{
                    border-bottom: 1px solid #ccc;
                    padding: 1em 0;
                }}
                .result-item:last-child {{
                    border-bottom: none;
                }}
                .title {{
                    margin-top: 1em;
                }}
                .wizard-img {{
                    width: 150px;
                    height: auto;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div>
                <img src="/wizard.png" alt="Wizard" class="wizard-img">
                <h1 class="title">The Oracle</h1>
            </div>
            <p>Ask the Oracle anything, and he shall... provide related links.</p>
            <form action="/query" method="get" class="query-box">
                <input type="text" name="q" value="{query}" placeholder="Type your search query, and then press 'Enter'..." required>
                <button type="submit">Search</button>
            </form>
        """

        if results is not None:
            html += '<div class="results">'
            if results:
                html += f"<p><b>Found {len(results)} matching documents:</b></p>"
                for result in results:
                    html += f"""
                    <div class="result-item">
                        <b>Rank:</b> {result['rank']}<br>
                        <b>Document:</b> 
                        <a href="/files/{result['document']}" target="_blank">{result['document']}</a><br>
                        <b>Score:</b> {result['score']:.4f}<br>
                        <b>Matching Terms:</b> {', '.join(result['terms'])}
                    </div>
                    """
            else:
                html += "<p>No matching documents found.</p>"
            html += "</div>"

        html += "</body></html>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

# run query and show results
    def handle_query(self, query):
        if not processor:
            self.serve_frontend(query="Error: QueryProcessor not initialized.")
            return

        params = parse_qs(query)
        user_query = params.get("q", [""])[0].strip()

        if not user_query:
            self.serve_frontend(query="Error: Query cannot be empty.")
            return

        results_data = processor.process_query(user_query)
        results = [
            {
                "rank": i,
                "document": doc_name,
                "score": score,
                "terms": terms
            }
            for i, (doc_name, score, terms) in enumerate(results_data, start=1)
        ]

        self.serve_frontend(results=results, query=user_query)

# run sever on 8080
def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, CustomHandler)
    print(f"Serving on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
