import demo
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
#parse tree

@app.route("/")
def helloWorld():
  return "hello from Flask!"

@app.route("/lesson")
def get_lesson():
  difficulty = request.args.get('difficulty')
  type = request.args.get('type')
  lessons = demo.get_lessons2(type, difficulty)
  return lessons
  
@app.route("/lesson-hardmode")
def get_hardmode():
  lessons = demo.get_hardmode('easy')
  return lessons

@app.route("/hardmode-node", methods = ['POST'])
def get_hardmode_node():
  function_name = request.args.get('func')
  cat = request.args.get('cat')
  node_id = request.args.get('node-id')
  correctNodes = request.get_json()
  subtree = demo.get_hardmode_node(function_name, node_id, correctNodes)
  nodes = subtree[0]
  edges = subtree[1]
  return [nodes, edges]

@app.route("/hardmode-correct")
def get_hardmode_correct():
  expr = request.args.get('expr')
  return


#ubona ukhamba olukhulu
#umfana unjengoyise