from flask import Flask, jsonify
from generate_unconditional_samples import generate_post

app = Flask(__name__)

TITLE_DELIMITER = "<|endoftitle|>"
ENTRY_DELIMITER = "<|endoftext|>"

@app.route("/generate", methods=['GET'])
def generate():
  # call on the model to generate a sample, and return the result
  # we can separate the title and body here as well, before sending it to the client

  post = generate_post()
  post = post.split(TITLE_DELIMITER)

  title = ""
  body = ""
  if len(post) > 1:
    title = post[0]
    body = "".join(post[1:])
  else:
    body ="".join(post)

  return jsonify(
    title=title,
    body=body
  )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=105)