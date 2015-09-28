import os, glob, json, codecs

F_SEARCH = sorted(glob.glob("search_data/*"))

def load_word_file(f):
    with codecs.open(f,'r','utf-8') as FIN:
        js = json.loads(FIN.read())
    return js

for f in F_SEARCH:
    js = load_word_file(f)

    try:
        js["items"] = [item["full_name"] for item in js["items"]]
    except:
        print "{} looks to be collated already".format(f)
        continue

    with codecs.open(f,'w','utf-8') as FOUT:
        FOUT.write(json.dumps(js))
            
    print "Completed {}".format(f)

    
