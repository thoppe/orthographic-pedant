import os, glob, json, codecs, time
from src.word_fix import fix_repo

# Ignore search results that have more than these number, they may
# represent github's automatic "fixes".
big_word_count = 500

# Load the blacklisted users, these users WON'T be checked.
BLACKLIST = {}
with open("blacklists/users.txt") as FIN:
    BLACKLIST["users"] = set()
    for line in FIN:
        BLACKLIST["users"].add(line.strip())

# Load the submissions, for now everybody only gets one!
with open("logs/submitted.log") as FIN:
    BLACKLIST["submitted"] = set()
    for line in FIN:
        word, name, submit_time = line.split()
        BLACKLIST["submitted"].add(name)

# Use the parsed version
#f_wordlist = "wordlists/wikipedia_list.txt"
f_wordlist = "wordlists/parsed_wikipedia_list.txt"    

FLAG_USING_FILTER = False

# Total number of corrections to run in one batch
#max_total_corrections = 20**10
max_total_corrections = 1

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
with open(f_wordlist) as FIN:
    for line in FIN:
        bad, good = line.strip().split('->')

        # Skip words with multiple mappings
        if ',' in good: continue

        # Skip words that aren't in clean list
        #if FLAG_USING_FILTER:
        #    if bad not in filter_words: continue
        
        corrections[bad] = good


def load_word_file(f):
    with codecs.open(f,'r','utf-8') as FIN:
        js = json.loads(FIN.read())
    return js

total_corrections = 0

for f in F_SEARCH:

    # Keep track of the "no-edits", this may mark github's autocorrect
    no_edit_counter = 0
    
    if total_corrections > max_total_corrections:
        break
    
    js = load_word_file(f)

    count = js["total_count"]
    word = f.split('/')[-1]
    
    if not count:
        continue

    if count > big_word_count:
        #print "BIG WORD COUNT...", f, count
        continue

    if word not in corrections:
        #print "Word {} not in corrections, skipping".format(word)
        continue
            
    if len(word) <= 3:
        print "Word '{}' too short, skipping".format(word)
        continue
        
    print "** Starting word {} ({}) **".format(word,count)

    for full_name in js["items"]:
        key = (word, full_name)

        user_name, repo_name = full_name.split('/')

        if user_name in BLACKLIST["users"]:
            msg = "Skipping {}. User on the blacklist."
            print msg.format(user_name)
            continue

        if key in LOGS:
            print "{} {} already completed, skipping".format(*key)
            continue

        if full_name in BLACKLIST["submitted"]:
            msg = "Skipping {}. User/repo already submitted."
            print msg.format(full_name)
            continue

        # Simple check for other spelling bots
        if "spell" in repo_name.lower():
            continue

        bad_word = word
        good_word = corrections[bad_word]

        # This case would be an intentional "typo"
        if bad_word in repo_name or bad_word in user_name:
            continue
        
        print "Starting {} {} -> {}".format(full_name, bad_word, good_word)
        
        pull_status = fix_repo(full_name, good_word, bad_word)

        log_item = "{} {} {}\n"
        F_LOG.write(log_item.format(word, full_name, int(time.time())))

        if not pull_status:
            no_edit_counter += 1
            
        if no_edit_counter >= 1:
            break

        total_corrections += 1



F_LOG.close()
