

'''
def load_word_file(f):
    with open(f) as FIN:
        js = json.loads(FIN.read())
    return js

f_wordfile = os.path.join("search_data",bad_word)
js = load_word_file(f_wordfile)
print len(js["items"])
repo = js["items"][0]
full_name = repo["full_name"]
'''
