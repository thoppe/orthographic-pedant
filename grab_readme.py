import requests

url = "https://api.github.com/search/repositories?q={query_string}"
params = {"language":"assembly",
          "sort":"stars",
          "order":"desc"}

r = requests.get(url.format(query_string="tetris"),params=params)
print r.text
