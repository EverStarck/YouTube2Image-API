import requests as r
import re
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
app = Flask(__name__)

@app.route('/info')
def data():
    # Get the youtube url from query arguments
    ytUrl = request.args.get('url')

    html = r.get(ytUrl).content
    # Get just the tittle
    tittle = BeautifulSoup(html, "html.parser").find('title')
    tittle = str(tittle)

    # Check if the Youtube channel exist
    if tittle == "<title>404 Not Found</title>":
        return jsonify("Error, youtube channel doesn't exist")
    else:
        #Get the script tag with all the data ([9] looks well)
        scriptGetter = BeautifulSoup(html, "html.parser").findAll('script', attrs={'nonce': re.compile('[\w\W]+')})[32]

        scriptToText = str(scriptGetter)
        #Get just the obj
        obj = re.split(r"<script nonce=\"(?:[^\"]+)\">var ytInitialData = ({.+});<\/script>", scriptToText)[1]
        jsonData = json.loads(obj)

        myData = {
            "banner": jsonData['header']['c4TabbedHeaderRenderer']['tvBanner']['thumbnails'],
            "avatar": jsonData['metadata']['channelMetadataRenderer']['avatar']['thumbnails'],
            "channelUrl": jsonData['metadata']['channelMetadataRenderer']['channelUrl'],
            "channelInfo": {
                "subs": jsonData['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText'],
                "title:": jsonData['metadata']['channelMetadataRenderer']['title'],
                "description": jsonData['metadata']['channelMetadataRenderer']['description'],
                "keywords": jsonData['metadata']['channelMetadataRenderer']['keywords'],
                "isFamilySafe": jsonData['metadata']['channelMetadataRenderer']['isFamilySafe'],
            }
        }

        return jsonify(myData)


if __name__ == "__main__":
    app.run(debug=True)
