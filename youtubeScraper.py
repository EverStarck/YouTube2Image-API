import requests as r
import re
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
# import time

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*.everstarck.com"}})
CORS(app)



@app.route('/info')
def data():
    # Get the youtube url from query arguments
    ytUrl = request.args.get('url')

    #start_time = time.time()

    # Get html of the request
    html = r.get(ytUrl, headers=headers).content
    soap = BeautifulSoup(html, "html.parser")

    # Get just the title
    title = str(soap.find('title'))

    # Check if the Youtube channel exist
    if title == "<title>404 Not Found</title>" or title == "<title>YouTube</title>" or title == "None" or ytUrl.find(".com/watch") != -1:
        return jsonify("Error, youtube channel doesn't exist")
    else:
        # Get the script tag with all the data ([9] looks well)
        scriptGetter = str(soap.findAll(
            'script', attrs={'nonce': re.compile('[\w\W]+')})[32])

        # Get just the obj
        obj = re.split(
            r"<script nonce=\"(?:[^\"]+)\">var ytInitialData = ({.+});<\/script>", scriptGetter)[1]

        # Obj to json
        jsonData = json.loads(obj)

        # Pass the data to own object
        metadata = jsonData['metadata']['channelMetadataRenderer']
        header = jsonData['header']['c4TabbedHeaderRenderer']

        # Check if the channel has banner
        if not header.get("tvBanner"):
            banner = [{"height": 1080, "url": "https://yt3.ggpht.com/p4M29lzrGdPQF_fBH1I1R9p_8Kjgjbnhm7orCzCO23Nxk-Hyv1dV01fzjWEQSljASvTjk6ez=w1920-fcrop64=1,00000000ffffffff-k-c0xffffffff-no-nd-rj", "width": 1920}]

        else:
            banner = header['tvBanner']['thumbnails']

        myData = {
            "banner": banner,
            "avatar": metadata['avatar']['thumbnails'],
            "channelUrl": metadata['channelUrl'],
            "channelInfo": {
                "subs": header['subscriberCountText']['simpleText'],
                "title": metadata['title'],
                "description": metadata['description'],
                "keywords": metadata['keywords'],
                "isFamilySafe": metadata['isFamilySafe'],
            }
        }

        #elapsed_time = time.time() - start_time
        # print(elapsed_time)

        return jsonify(myData)


if __name__ == "__main__":
    app.run(debug=True)
