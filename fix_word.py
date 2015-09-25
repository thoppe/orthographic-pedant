import os, json, logging, glob, codecs, os, time, subprocess
from contextlib import contextmanager
import requests
logging.basicConfig(level=logging.INFO)

## TO DO:
## CREATE PULL REQUEST!
## DELETE FORK
## LOG AS COMPLETE!

# Verify that there is a token set as an env variable and load it
shell_token  = "GITHUB_ORTHOGRAPHIC_TOKEN"
GITHUB_TOKEN = os.environ[shell_token]
login_params = {"access_token":GITHUB_TOKEN,}


API_URL    = "https://api.github.com/repos"
fork_url   = API_URL + "/{user_name}/{repo_name}/forks"
pulls_url = API_URL + "/{user_name}/{repo_name}/pulls"
delete_url = API_URL + "/{user_name}/{repo_name}"
clone_url  = "https://github.com/orthographic-pedant/{repo_name}"

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

def set_local_permission():
    # Set the local username
    cmd = 'git config user.name "orthographic-pendant"'
    os.system(cmd)

    # Set the password
    cmd = 'git config url."https://orthographic-pendant:{access_token}@github.com".insteadOf "https://github.com"'
    os.system(cmd.format(**repo))



@contextmanager
def enter_repo(repo):

    # Remember our original directory
    org_dir = os.getcwd()

    f_url = fork_url.format(**repo)

    # Create the fork!
    #r = requests.post(f_url,params=login_params)
    #logging.info("Creating fork, status {}".format(r))
    #logging.info("Sleeping for 10")
    #time.sleep(10)

    # Create the directories
    os.system("mkdir -p forks")
    os.chdir("forks")

    repo["full_name"] = "{user_name}:{repo_name}".format(**repo)

    cmd = "git clone " + clone_url.format(**repo)
    if not os.path.exists(repo["repo_name"]):
        msg = "Cloning repo {full_name}".format(**repo)
        logging.info(msg)
        os.system(cmd)

    os.chdir(repo["repo_name"])
    logging.info("Entered {}".format(repo["full_name"]))

    yield
    
    logging.info("Exiting {}".format(repo["full_name"]))
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
repo = {
    "user_name": "thoppe",
    "repo_name": "I-am-error",
    "access_token":GITHUB_TOKEN,
}
        
with enter_repo(repo):

    # Find READMES
    F_README = [x for x in glob.glob("*.*")
                if 'readme.' in x.lower()]

    # Get the current branch name
    p = subprocess.check_output("git show-branch",shell=True)
    repo["master_branch"] = p.split(']')[0][3:]

    # Create a new branch
    repo["branch_name"] = "spell_check/{}".format(good_word)
    cmd = "git checkout -b {branch_name}".format(**repo)
    os.system(cmd)
    
    # Fix READMES
    for fr in F_README:
        fix_file(fr, bad_word, good_word)

    # Commit changes
    msg = 'Fixed typographical error, changed {} to {} in README.'
    msg = msg.format(bad_word, good_word)
    cmd = 'git commit -a -m "{}"'.format(msg)
    os.system(cmd)

    # Push the changes to bot directory
    set_local_permission()
    logging.info("Pushing to new branch")
    cmd = "git push origin {branch_name}".format(**repo)
    os.system(cmd)

    # Create pull request
    data = {
        "head"  :"orthographic-pendant:{branch_name}".format(**repo),
        "base"  : repo["master_branch"],
        "title" : msg,
        "body"  : '''
        {user_name}, I've corrected a typo in the documentation of the 
        {repo_name} project. If this was intentional or you enjoy living in 
        linguistic squalor please let me know and create an issue on
        https://github.com/thoppe/orthographic-pedant.        
        '''.strip().format(**repo)
    }
    data["body"] = "base"
    print json.dumps(data,indent=2)

    f_url = pulls_url.format(**repo)
    print f_url
    r = requests.post(f_url,data=data)
    print r
    print r.content
    exit()
    #logging.info("Creating fork, status {}".format(r))
    #logging.info("Sleeping for 10")
    #time.sleep(10)

    print "HI!"

