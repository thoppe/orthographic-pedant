import os

# Verify that there is a token set as an env variable
shell_token  = "GITHUB_ORTHOGRAPHIC_TOKEN"
GITHUB_TOKEN = os.environ[shell_token]

import requests, os, json, codecs, time, pprint
from datetime import datetime

# github's search API
url = "https://api.github.com/search/repositories"

WORDS = []
with open("wordlists/wikipedia_list.txt") as FIN:
    for line in FIN:
        WORDS.append(line.split('-')[0])

for word in WORDS:

    f_word = os.path.join("search_data",word)
    if os.path.exists(f_word):
        print word,"already exists skipping"
        continue

    params = {
        "q" : word+'+in:readme+stars:>1+file:',
        "sort":"stars",
        "order":"desc",
        "per_page":100,
        "access_token":GITHUB_TOKEN,
    }
    payload_str = "&".join("%s=%s" % (k,v) for k,v in params.items())
    r = requests.get(url,params=payload_str)
    js = r.json()

    with codecs.open(f_word,'w','utf-8') as FOUT:
        FOUT.write(json.dumps(js,indent=2))

    print word, js["total_count"]
    
    limit = int(r.headers["x-ratelimit-remaining"])
    #print "x-remaining-remaining", limit
    #pprint.pprint(dict(r.headers))

    utc_reset_time = int(r.headers["x-ratelimit-reset"])
    reset_time = datetime.utcfromtimestamp(utc_reset_time)
    
    if limit < 2:


        now_time = datetime.utcnow()
        delta_seconds = (reset_time - now_time).total_seconds()

        if delta_seconds < 0: break

        print "Sleeping {:0.3f} seconds for API limit.".format(delta_seconds)
        time.sleep(delta_seconds)


