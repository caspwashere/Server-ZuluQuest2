from flask import render_template, url_for, request,jsonify, json, after_this_request, send_file
import base64
import io
import demo
import random

# from sanic.response import text
# from sanic import json,file, Sanic
# from sanic_ext import Extend

# app = Sanic("GrammarAPI")
# app.config.CORS_ORIGINS = "http://localhost:5173/"
# Extend(app)

# @app.route("/file")
# async def handler(request):
#     return await file("./test.gv.png", mime_type="image/png")

# @app.get("/")
# async def hello_world(request):
#     return json({"foo": "bar"})

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
#parse tree

@app.route("/")
def helloWorld():
  return ""


@app.route("/random_phrase")
def gen_phrase():
  
  return demo.read_db(0, 'scramble')

@app.route("/random_tree")
def get_tree():
 # return demo.read_AST(0, 'builder')
  return demo.get_lessons2()[2]

@app.route("/lesson")
def get_lesson():
  difficulty = request.args.get('difficulty')
  type = request.args.get('type')
  print(difficulty)
  if difficulty == 'easy':
    return demo.get_lessons2(type)[0]
  elif difficulty =='medium':
    return demo.get_lessons2(type)[1]
  elif difficulty =='hard':
    return demo.get_lessons2(type)[2]
 


#dlalani kamnandi bafana is a problem
#mbize ntombi
#yisalukazi sodwa esihlala ekhaya
#umfazi upheka manje
#sithanda ukudla
#umlilo ushisa kabi
#umfazi upheka ukudla
#izintombi zitheza ehlathini
#ubona ukhamba olukhulu
#umfazi ubiza umfana
#abafana bala ukudlala
#izimvu zasinda kodwa izinkomo zona zafa