import os, glob, json, codecs, time
from src.word_fix import fix_repo

# Total number of corrections to run in one batch
max_total_corrections = 20

os.system("mkdir -p logs")
F_SEARCH = sorted(glob.glob("search_data/*"))

# Create (or append a log file)
f_logfile = "logs/submitted.log"

# Read logfile into memory
with open(f_logfile,'r') as FIN:
    LOGS = []
    for line in FIN:
        word, full_name, timestamp = line.split()
        LOGS.append((word,full_name))
    LOGS = set(LOGS)

# Open the logfile for appending
F_LOG = open(f_logfile,'a')

# Load the wordlist
corrections = {}
with open("wordlists/wikipedia_list.txt") as FIN:
    for line in FIN:
        bad, good = line.strip().split('->')

        # Skip words with multiple mappings
        if ',' in good: continue
        corrections[bad] = good

def load_word_file(f):
    with codecs.open(f,'r','utf-8') as FIN:
        js = json.loads(FIN.read())
    return js

total_corrections = 0

for f in F_SEARCH:
    if total_corrections > max_total_corrections:
        break
    
    js = load_word_file(f)
    count = js["total_count"]
    word = f.split('/')[-1]
    
    if not count: continue

    if count > 500:
        print "BIG WORD COUNT...", f, count
        continue

    if word not in corrections:
        print "Word {} not in corrections, skipping".format(word)
        continue
            
    
    if len(word) <= 3:
        print "Word '{}' too short, skipping".format(word)
        continue
        
    print "** Starting word {} ({}) **".format(word,len(js["items"]))

    for full_name in js["items"]:
        key = (word, full_name)

        if key in LOGS:
            print "{} {} already completed, skipping".format(*key)
            continue


        bad_word = word
        good_word = corrections[bad_word]
        print "Starting {} {} -> {}".format(full_name, bad_word, good_word)
        fix_repo(full_name, good_word, bad_word)

        log_item = "{} {} {}\n"
        F_LOG.write(log_item.format(word, full_name, int(time.time())))

        total_corrections += 1



F_LOG.close()
