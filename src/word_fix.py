import os, json, logging, glob, codecs, os, time, subprocess
from contextlib import contextmanager
import requests
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

FLAG_fork = True
FLAG_delete = True

fork_sleep_time = 8

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


pull_request_msg = ' '.join('''
  {user_name}, I've corrected a typographical error in the documentation of the 
  [{repo_name}](https://github.com/{user_name}/{repo_name})
  project. You should be able to merge this pull request automatically. 
  However, if this was intentional or you enjoy living in 
  linguistic squalor please let me know and 
  [create an issue](https://github.com/thoppe/orthographic-pedant/issues/new)
  on my home repository.
'''.split())

def is_branch_different_from_default(repo):
    # Checks if any substantial commits have been made
    cmd = "git diff {master_branch} --".format(**repo)
    
    p = subprocess.check_output(cmd,shell=True).strip()

    # If any edits have been made this will return True
    return p


def pull_request_repo(repo):

    if not is_branch_different_from_default(repo):
        logging.info("No edits have been made, skipping!".format(**repo))
        return

    logging.info("Creating pull request for {full_name}".format(**repo))

    data = {
        "head"  :"{bot_name}:{branch_name}".format(**repo),
        "base"  : repo["master_branch"],
        "title" : repo["fix_msg"],
        "body"  : pull_request_msg.format(**repo),
    }

    url = pulls_url.format(**repo)
    r = requests.post(url,params=login_params,json=data)
    if "errors" in r.json():
        from pprint import pprint
        print pprint(r.json()["errors"])
        
    logging.info("Pull request status {}".format(r))


def fork_repo(repo):
    f_url = fork_url.format(**repo)
    r = requests.post(f_url,params=login_params)
    status = r.status_code
    logging.info("Creating fork, status {}".format(status))
    
    assert(status == 202)
    logging.info("Sleeping for {} seconds.".format(fork_sleep_time))
    time.sleep(fork_sleep_time)

def push_commits(repo):
    logging.info("Push new branch {bot_name}:{branch_name}".format(**repo))
    cmd = "git push -u " + push_url.format(**repo)
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


@contextmanager
def enter_repo(repo):

    # Remember our original directory
    org_dir = os.getcwd()

    repo["bot_name"] = "orthographic-pedant"
    repo["bot_password"] = GITHUB_TOKEN
    repo["bot_email"] = "https://github.com/thoppe/orthographic-pedant/issues/new"

    # Record the full name of the repo
    repo["full_name"] = "{user_name}:{repo_name}".format(**repo)

    logging.info("Entered {}".format(repo["full_name"]))
    
    if FLAG_fork:
        fork_repo(repo)

    # Create the directories
    os.system("mkdir -p forks")
    os.chdir("forks")

    clone_repo(repo)

    # Enter the repo directory
    os.chdir(repo["repo_name"])

    # Get the current branch name
    p = subprocess.check_output("git show-branch",shell=True)
    repo["master_branch"] = p.split(']')[0].split('[')[1]

    # Set the username
    cmd = 'git config user.name "{bot_name}"'.format(**repo)
    os.system(cmd)
    cmd = 'git config user.email "{bot_email}"'.format(**repo)
    os.system(cmd)

    yield
    
    logging.info("Exiting {}".format(repo["full_name"]))

    if FLAG_delete:
        delete_bot_repo(repo)
    
    os.chdir(org_dir)
    os.system("rm -rf forks")

def fix_repo(full_name, good_word, bad_word):

    full_name = full_name.strip()
    user_name, repo_name = full_name.split('/')

    repo = {
        "access_token" : GITHUB_TOKEN,
        "user_name" : user_name,
        "repo_name" : repo_name,
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
        repo["fix_msg"] = 'Fixed typographical error, changed {} to {} in README.'
        repo["fix_msg"] = repo["fix_msg"].format(bad_word, good_word)
        cmd = 'git commit -a -m "{fix_msg}"'.format(**repo)
        os.system(cmd)

        # Push the changes to bot directory
        push_commits(repo)

        # Create pull request
        pull_request_repo(repo)


###############################################################


if __name__ == "__main__":

    # Target word
    bad_word  = "Celcius"
    good_word = "Celsius"
    full_name = "thoppe/I-am-error"

    fix_repo(full_name, good_word, bad_word)
        
