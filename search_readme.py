import os

# Verify that there is a token set as an env variable
shell_token  = "GITHUB_ORTHOGRAPHIC_TOKEN"
GITHUB_TOKEN = os.environ[shell_token]

import requests, os, json, codecs, time

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
        "q" : word+'+in:readme+stars:>1',
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
    print "x-remaining-remaining", limit
    
    if limit < 2:
        print "Sleeping for API limit."
        time.sleep(60)
        
    time.sleep(1)
