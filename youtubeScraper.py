import requests as r
import re
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
# import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
app = Flask(__name__)
CORS(app)

@app.route('/info')
def data():
    # Get the youtube url from query arguments
    ytUrl = request.args.get('url')

    #start_time = time.time()

    #Doc parser
    html = r.get(ytUrl).content
    soap = BeautifulSoup(html, "html.parser")

    # Get just the title
    title = str(soap.find('title'))

    # Check if the Youtube channel exist
    if title == "<title>404 Not Found</title>" or title == "<title>YouTube</title>" or title == "None" or ytUrl.find(".com/watch") != -1:
        return jsonify("Error, youtube channel doesn't exist")
    else:
        #Get the script tag with all the data ([9] looks well)
        scriptGetter = str(soap.findAll('script', attrs={'nonce': re.compile('[\w\W]+')})[32])

        #Get just the obj
        obj = re.split(r"<script nonce=\"(?:[^\"]+)\">var ytInitialData = ({.+});<\/script>", scriptGetter)[1]

        #Obj to json
        jsonData = json.loads(obj)

        #Pass the data to own object
        metadata = jsonData['metadata']['channelMetadataRenderer']
        header = jsonData['header']['c4TabbedHeaderRenderer']

        #Check if the channel has banner
        if not header.get("tvBanner"):
            banner = [{"height":1080,"url":"https://yt3.ggpht.com/p4M29lzrGdPQF_fBH1I1R9p_8Kjgjbnhm7orCzCO23Nxk-Hyv1dV01fzjWEQSljASvTjk6ez=w1920-fcrop64=1,00000000ffffffff-k-c0xffffffff-no-nd-rj","width":1920}]

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
        #print(elapsed_time)

        return jsonify(myData)


if __name__ == "__main__":
    app.run(debug=True)
