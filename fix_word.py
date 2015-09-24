import os, json, logging, glob, codecs
logging.basicConfig(level=logging.INFO)
from contextlib import contextmanager


# TO DO
# Create proper fork
# POST /repos/:owner/:repo/forks
## TO DO:
## push...
## MARK PUSHED
## remove


# Target word
bad_word  = "Celcius"
good_word = "Celsius"

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


@contextmanager
def enter_repo(full_name):

    # Remember our original directory
    org_dir = os.getcwd()

    # Set the local username
    cmd = 'git config user.name "orthographic-pendant"'
    os.system(cmd)
    os.system('git config user.name')

    user_name,repo_name = full_name.split('/')

    # Create the directories
    os.system("mkdir -p forks")
    os.chdir("forks")

    os.system("mkdir -p {}".format(user_name))
    os.chdir(user_name)

    cmd = "git clone {clone_url}".format(**repo)
    if not os.path.exists(repo_name):
        print "Cloning repo", full_name
        os.system(cmd)

    os.chdir(repo_name)
    
    logging.info("Entered {}".format(full_name))
    yield
    logging.info("Exiting {}".format(full_name))
    os.chdir(org_dir)   
    

def fix_word(line,w1,w2):
    line = line.replace(w1.title(),w2.title())
    line = line.replace(w1,w2)
    line = line.replace(w1.lower(),w2.lower())
    return line

def fix_file(f, w1, w2):
    newlines = []
    with codecs.open(f,'r','utf-8') as FIN:
        for line in FIN:
            while w1.lower() in line.lower():
                logging.info("Fixing {} in {}".format(w1,f)) 
                line = fix_word(line,w1,w2)
            newlines.append(line)
            
    with codecs.open(f,'w','utf-8') as FOUT:
        FOUT.write(''.join(newlines))
                


#full_name = "orthographic-pedant/I-am-error"
full_name = "thoppe/I-am-error"
repo = {"clone_url": "https://orthographic-pendant@github.com/" + full_name}
        
with enter_repo(full_name):

    # Find READMES
    F_README = [x for x in glob.glob("*.*")
                if 'readme.' in x.lower()]

    # Create a new branch
    branch = "spell_check/{}".format(good_word)
    cmd = "git checkout -b {}".format(branch)
    os.system(cmd)

    # Create upstream
    cmd = "git remote add upstream {clone_url}".format(**repo)
    print cmd
    exit()
    #cmd = "git remote add upstream https://github.com/omeka/Omeka.git"
    #spell_check/{}".format(good_word)

    # Fix READMES
    for fr in F_README:
        fix_file(fr, bad_word, good_word)

    # Commit changes
    msg = 'Fixed typographical error, changed {} to {} in README.'
    cmd = 'git commit -a -m "{}"'.format(msg.format(bad_word, good_word))
    os.system(cmd)

    # Push?
    cmd = "git push origin {}".format(branch)
    os.system(cmd)

