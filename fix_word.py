import os, json, logging, glob, codecs, os, time, subprocess
from contextlib import contextmanager
import requests
logging.basicConfig(level=logging.INFO)

#GIT_EXEC = "hub/hub"
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
pulls_url  = API_URL + "/{user_name}/{repo_name}/pulls"
delete_url = API_URL + "/{user_name}/{repo_name}"
push_url   = "https://{bot_name}:{bot_password}@github.com/{bot_name}/{repo_name} {branch_name}:{branch_name}"

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

pull_request_msg = ' '.join('''
  {user_name}, I've corrected a typo in the documentation of the 
  {repo_name} project. If this was intentional or you enjoy living in 
  linguistic squalor please let me know and create an issue on
  https://github.com/thoppe/orthographic-pedant.
'''.split())

def pull_request_repo(repo):
    data = {
        "head"  :"orthographic-pendant:{branch_name}".format(**repo),
        "base"  : repo["master_branch"],
        "title" : msg,
        "body"  : pull_request_msg.format(**repo),
    }

    print json.dumps(data,indent=2)
    url = pulls_url.format(**repo)
    exit()

    r = requests.post(f_url,
                      params=login_params,
                      json=data)
    print r
    print r.content


    pass


def fork_repo(repo):
    f_url = fork_url.format(**repo)
    r = requests.post(f_url,params=login_params)
    status = r.status_code
    logging.info("Creating fork, status {}".format(status))
    
    assert(status == 202)
    logging.info("Sleeping for 10")
    time.sleep(10)

def push_commits(repo):
    logging.info("Push new branch {bot_name}:{branch_name}".format(**repo))
    cmd = "git push " + push_url.format(**repo)
    os.system(cmd)  

def clone_repo(repo):
    
    git_endpoint = clone_url.format(**repo)
    cmd = "git clone -q " + git_endpoint

    if not os.path.exists(repo["repo_name"]):
        msg = "Cloning repo {full_name}".format(**repo)
        logging.info(msg)
        os.system(cmd)

def does_git_branch_exist(repo):
    # Checks if a branch already exists of a given name
    cmd = "git rev-parse -q --verify {branch_name}".format(**repo)
    try:
        p = subprocess.check_output(cmd,shell=True).strip()
    except subprocess.CalledProcessError:
        return False

    # Valid SHA1 hash will be forty characters long
    return len(p.strip()) == 40

def create_branch(repo):
    # Attempts to create the branch in repo["branch_name"]  

    if not does_git_branch_exist(repo):
        logging.info("Creating new branch {branch_name}".format(**repo))
        cmd = "git checkout -b {branch_name}".format(**repo)
        os.system(cmd)

def delete_bot_repo(repo):
    url = API_URL + "/{bot_name}/{repo_name}".format(**repo)
    r = requests.delete(url,params=login_params)
    msg = "Deleted bot repo {repo_name}, status {}"
    logging.info(msg.format(r.status_code,**repo))

@contextmanager
def enter_repo(repo):

    repo["bot_name"] = "orthographic-pedant"
    repo["bot_password"] = GITHUB_TOKEN

    # Record the full name of the repo
    repo["full_name"] = "{user_name}:{repo_name}".format(**repo)

    #delete_bot_repo(repo)

    # Remember our original directory
    org_dir = os.getcwd()

    # Create the fork!
    #fork_repo(repo)

    # Create the directories
    os.system("mkdir -p forks")
    os.chdir("forks")

    clone_repo(repo)

    # Enter the repo directory
    os.chdir(repo["repo_name"])
    logging.info("Entered {}".format(repo["full_name"]))

    # Get the current branch name
    p = subprocess.check_output("git show-branch",shell=True)
    repo["master_branch"] = p.split(']')[0].split('[')[1]

    yield
    
    logging.info("Exiting {}".format(repo["full_name"]))
    os.chdir(org_dir)   
    

def fix_word(line,w1,w2):
    line = line.replace(w1.title(),w2.title())
    line = line.replace(w1,w2)
    line = line.replace(w1.lower(),w2.lower())
    return line

def fix_file(f, w1, w2):
    corrections = 0
    newlines = []
    with codecs.open(f,'r','utf-8') as FIN:
        for line in FIN:
            while w1.lower() in line.lower():
                logging.info("Fixing {} in {}".format(w1,f)) 
                line = fix_word(line,w1,w2)
                corrections += 1
            newlines.append(line)
            
    with codecs.open(f,'w','utf-8') as FOUT:
        FOUT.write(''.join(newlines))
    return corrections
                


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

    repo["branch_name"] = "spell_check/{}".format(good_word)

    create_branch(repo)
    
    # Fix READMES
    total_corrections = 0
    for fr in F_README:
        total_corrections += fix_file(fr, bad_word, good_word)
    logging.info("Fixed {} spelling mistakes".format(total_corrections))

    # Commit changes
    msg = 'Fixed typographical error, changed {} to {} in README.'
    msg = msg.format(bad_word, good_word)
    cmd = 'git commit -a -m "{}"'.format(msg)
    os.system(cmd)

    # Push the changes to bot directory
    push_commits(repo)

    # Create pull request
    pull_request_repo(repo)
    exit()
    #logging.info("Creating fork, status {}".format(r))
    #logging.info("Sleeping for 10")
    #time.sleep(10)

    print "HI!"

