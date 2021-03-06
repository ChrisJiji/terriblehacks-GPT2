from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from generate_unconditional_samples import generate_post
from os.path import exists
import os
import json
from threading import Thread

app = Flask(__name__)
CORS(app, support_credentials=True)

TITLE_DELIMITER = "<|endoftitle|>"
ENTRY_DELIMITER = "<|endoftext|>"
POSTS_PATH = "saved_posts.json"
LOCK_PATH = "lock"

# idea is to keep a number of pre-generated posts, because it takes a while to
# generate and it seems that multiple posts are generated at once.
def refill_posts():
  # create lockfile to make sure only one thread is generating posts at once
  if exists(LOCK_PATH):
    print("thread denied >:(")
    return
  
  print("refilling posts")
  
  file = open(LOCK_PATH, 'w+')
  file.close()

  if not exists(POSTS_PATH):
    file = open(POSTS_PATH, 'w+')
    file.write("[]")
    file.close()
  
  saved_posts = []
  with open(POSTS_PATH, "r") as f:
    saved_posts = json.load(f)
  
  if not saved_posts:
    saved_posts = []
  
  changed = False
  
  # if we have less than 20 posts, generate more until we have 30 saved
  if len(saved_posts) < 20:
    print("generating more posts...")
    changed = True
    while len(saved_posts) < 30:
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
        
        # remove unnecessary newlines
        while title and title[0] == "\n":
          title = title[1:]
        while body and body[0] == "\n":
          body = body[1:]      
        while title and title[-1] == "\n":
          title = title[:-1]
        while body and body[-1] == "\n":
          body = body[:-1]

        # skip empty posts
        if not title and not body:
          continue

        saved_posts.append({
          "title": title,
          "body": body
        })
      
      print("number of saved posts:", len(saved_posts))
  
  # save the new set of generated posts
  if changed:
    with open(POSTS_PATH, "w") as f:
      json.dump(saved_posts, f)

  os.remove(LOCK_PATH)

# retrieve one post from our stash of pre-generated posts
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

# 'generate' endpoint that gives one post to the client
@app.route("/generate", methods=['GET'])
@cross_origin(supports_credentials=True)
def generate():

  post = get_post()
  
  thread = Thread(target=refill_posts)
  thread.start()

  return jsonify(post)
  

# no longer necessary, was just to get it started
@app.route("/refillllllllllllllllllllllllllllllllll", methods=['GET'])
@cross_origin(supports_credentials=True)
def refillllllllllllllllllllllllllllllllll():
  thread = Thread(target=refill_posts)
  thread.start()

  return "generating posts"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=105)
