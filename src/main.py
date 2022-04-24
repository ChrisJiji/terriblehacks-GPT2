from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from generate_unconditional_samples import generate_post
from os.path import exists
import os
import json
import time
from threading import Thread

app = Flask(__name__)
CORS(app, support_credentials=True)

TITLE_DELIMITER = "<|endoftitle|>"
ENTRY_DELIMITER = "<|endoftext|>"
POSTS_PATH = "saved_posts.json"
LOCK_PATH = "lock"

def refill_posts():
  #create lockfile to prevent multiple threads
  if exists(LOCK_PATH):
    print("thread denied >:(")
    return
  
  print("thread created")
  
  file = open(LOCK_PATH, 'w+')
  file.close()

  if not exists(POSTS_PATH):
    file = open(POSTS_PATH, 'w+')
    file.write("[]")
    file.close()
  print("generating more posts...")
  
  saved_posts = []
  with open(POSTS_PATH, "r") as f:
    saved_posts = json.load(f)
  
  if not saved_posts:
    saved_posts = []
  
  while len(saved_posts) < 20:
    raw_posts = generate_post()
    raw_posts = raw_posts.split(ENTRY_DELIMITER)

    for p in raw_posts:
      p = p.split(TITLE_DELIMITER)
      title = ""
      body = ""
      if len(p) > 1:
        title = p[0]
        body = "".join(p[1:])
      else:
        title = "idk"
        body = "".join(p)
      
      while title and title[0] == "\n":
        title = title[1:]
      while body and body[0] == "\n":
        body = body[1:]      
      while title and title[-1] == "\n":
        title = title[:-1]
      while body and body[-1] == "\n":
        body = body[:-1]

      if not title and not body:
        continue

      saved_posts.append({
        "title": title,
        "body": body
      })
    
    print("number of saved posts:", len(saved_posts))
  
  with open(POSTS_PATH, "w") as f:
    json.dump(saved_posts, f)

  os.remove(LOCK_PATH)

def get_post():
  saved_posts = []
  with open(POSTS_PATH, "r") as f:
    saved_posts = json.load(f)
  
  if not saved_posts or len(saved_posts) == 0:
    return {
      "title": "where shitposts?",
      "body": "no more shitposts :("
    }

  post = saved_posts[0]
  saved_posts = saved_posts[1:]

  with open(POSTS_PATH, "w") as f:
    json.dump(saved_posts, f)
  
  return post


@app.route("/generate", methods=['GET'])
@cross_origin(supports_credentials=True)
def generate():

  post = get_post()
  
  thread = Thread(target=refill_posts)
  thread.start()

  return jsonify(post)
  

@app.route("/refillllllllllllllllllllllllllllllllll", methods=['GET'])
@cross_origin(supports_credentials=True)
def refillllllllllllllllllllllllllllllllll():
  thread = Thread(target=refill_posts)
  thread.start()

  return "generating posts"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=105)
