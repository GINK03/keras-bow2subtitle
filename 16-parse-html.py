import bs4

import glob

import os

import dbm

import pickle


import concurrent.futures


def _map(arr):
  key, names = arr
  db = dbm.open("16-parsed_{key}.dbm".format(key=key), "c")
  for name in names:
    soup = bs4.BeautifulSoup(open(name).read())
    [s.extract() for s in soup('script')]
    
    title_parts = soup.find("div", {"class":"title-parts"})
    if title_parts is None:
      continue

    title = title_parts.find("h1")
    subtitle = title_parts.find("h2")

    if title is None or subtitle is None:
      os.remove(name)
      continue
    
    date = soup.find("meta", property="article:published_time")
    print(date.get("content"))
    body = soup.find("div", {"id":"article-body-inner"})
    #print(name.replace("_","/"))
    key = name.split("/").pop().replace("_","/")
    val = { "title": title.text, 
            "subtitle": subtitle.text,
            "date": date.get("content"),
            "body": body.text.strip() }
    print(key,val)
    db[ key ] = pickle.dumps(val)

arrs = {}
for index, name in enumerate(glob.glob("htmls/*")):
  key = index%16
  if arrs.get(key) is None:
    arrs[key] = []
  arrs[key].append( name )
arrs = [(key, names) for key, names in arrs.items() ]
#_map(arrs[0])
with concurrent.futures.ProcessPoolExecutor(max_workers=16) as exe:
  exe.map(_map, arrs)
