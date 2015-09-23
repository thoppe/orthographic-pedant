import glob, json
import numpy as np

F_WORDS = sorted(glob.glob("search_data/*"))

def load_word_file(f):
    with open(f) as FIN:
        js = json.loads(FIN.read())
    return js

SIZE = []
for f in F_WORDS:
    try:
        js = load_word_file(f)
    except:
        print "Problem with", f
        continue
    x = js["total_count"]

    if x>50 and x<500:
        SIZE.append(x)
        #print f, x
    if x>20000:
        print f,x 
            

SIZE = np.array(SIZE)
SIZE = SIZE[SIZE<1000]

import seaborn as sns
sns.distplot(SIZE)
sns.plt.show()
