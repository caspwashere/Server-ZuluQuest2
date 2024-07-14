import pgf, pgfaux
import pgfaux.analyze as an
import pgfaux.generate as gen
import pgfaux.exceptions as exceptions
import csv
import json
import re
import random
from graphviz import Source
import weight

grammar = pgf.readPGF("NguniDev.pgf")
zul = grammar.languages['DevLangZul']

def read_db(index, type):
    file = open('taljaard_bosch.parallel.csv')
    csv_reader = csv.reader(file)
    header = []
    header = next(csv_reader) 
    rows = []
    for row in csv_reader:
        rows.append(row)
    file.close()  


    r =random.randint(0, 127)
   
    # for row in rows:
    word_syllables = {}
    words = []
    syllables = []
    e = pgf.readExpr(rows[index+r][0])
    phrase = zul.linearize(e)
    syllables = convert_expr_to_string_syllables(e)
    #get_nr_of_words(row[1])
    nodes = []
    edges = []
    get_AST(e, nodes, edges, an.depth(e), 0, 0, 0, 0, type)
    # print('Nodes '+ str(nodes)+'\n\n')
    
    # print('Edges ' + str(edges))
    words = get_words(rows[index+r][1])
    create_pairs(words, syllables, word_syllables)
    return [phrase, word_syllables, syllables, nodes, edges]

def convert_expr_to_string_syllables(e):
    [b] = zul.bracketedLinearize(e)
    temp =  str(b)
    pattern = r"\b\w+:\w+\b"
    # Replacing the matched pattern with an empty string
    output_string = re.sub(pattern, '', temp)
    output_string = output_string.replace('(', '').replace(')', '').split(' ')
    result = [] 
    for i in output_string: 

        if i != '': 
            result.append(i) 
    return result

def create_pairs(words, syllables, word_syllables):
    i = 0
    for j in range(len(words)):
        temp = ''
        syll = []
        i = 0
        # print('word: ',words[j])
        while i < len(syllables):
            temp += syllables[i]
            syll.append(syllables[i])
            if temp in word_syllables:
                temp = ''
                syll = []

            if temp == words[j]:
                
                word_syllables[words[j]] = syll
                temp = ''
                syll = []
            i += 1
           

    # print(word_syllables)
                       
def get_nr_of_words(entry):
    return entry.count(" ")+1

def get_words(entry):
    return entry.split(' ')

def get_AST(expr, nodes, edges, max_depth, curr_depth, node_id, offset, parent_node_id, type):

    if curr_depth > max_depth: return
    # print(expr)
    label = an.root_str(expr) + ":" + an.root_cat(expr, grammar)
    if (curr_depth == max_depth):
       if type =='builder':
            functions_by_cat = grammar.functionsByCat(an.root_cat(expr,grammar))
            nodes.append({
            'id': str(node_id),
            'data': {
                'label': label,
                'list': functions_by_cat,
            },
            'type': 'grammar-node',
            'position': {
                'x': curr_depth*100,
                'y':curr_depth*100,
            }
        })
       if type =='scramble':
           nodes.append({
            'id': str(node_id),
            'data': {
                'label': label
            },
            'type': 'custom-node',
            'position': {
                'x': curr_depth*100,
                'y':curr_depth*100,
            }
        })  
    else:
        nodes.append({
            'id': str(node_id),
            'data': {
                'label': label
            },
            'type': 'custom-node',
            'position': {
                'x': curr_depth*100,
                'y':curr_depth*100,
            }
        })
        
    
    if parent_node_id != node_id:
        edges.append({
            'id': str(parent_node_id)+'-'+str(node_id),
            'source': str(parent_node_id),
            'target': str(node_id),
            'type': 'custom-edge',
        })

    # print(label + ' at depth: ' + str(curr_depth))
    children = an.children_trees(expr)
    for child in children:
        offset += 1 + random.randrange(1,100)
        get_AST(child, nodes, edges, max_depth, curr_depth+1, node_id + offset, offset, node_id, type)

def read_AST(index, type):
    file = open('taljaard_bosch.parallel.csv')
    csv_reader = csv.reader(file)
    header = []
    header = next(csv_reader) 
    rows = []
    for row in csv_reader:
        rows.append(row)
    file.close() 
    r =random.randint(0, 127)

    e = pgf.readExpr(rows[index+r][0])
    phrase = zul.linearize(e)
    nodes = []
    edges = []
    get_AST(e, nodes, edges, an.depth(e), 0, 0, 0, 0, type)
    # s = Source(grammar.graphvizAbstractTree(e), filename="bafana", format="png")
    # s.view()
    print(nodes)
    print(edges)
    return [phrase, nodes, edges]


def gen_random_AST(starting_cat, depth):
    expr = gen.generate_random_tree_by_cat(grammar, starting_cat, depth)
    if expr:
        if zul.linearize(expr):
            l = zul.linearize(expr)
            print('expr! ' + l)
            if '[' not in l:
                i = zul.parse(l)
                p,e = i.__next__()
                print(e)
                return [l, e]
    else:
        return []


def get_lessons():
    file = open('taljaard_bosch.parallel.csv')
    csv_reader = csv.reader(file)
    header = []
    header = next(csv_reader) 
    rows = []
    for row in csv_reader:
        rows.append(row)
    file.close()  
    lessons = []
    easy = []
    medium = []
    hard = []
    for row in rows:
        word_syllables = {}
        words = []
        syllables = []
        e = pgf.readExpr(row[0])
        phrase = zul.linearize(e)
        syllables = convert_expr_to_string_syllables(e)
        #get_nr_of_words(row[1])
        nodes = []
        edges = []
        get_AST(e, nodes, edges, an.depth(e), 0, 0, 0, 0, 'scramble')
        # print('Nodes '+ str(nodes)+'\n\n')
        
        # print('Edges ' + str(edges))
        words = get_words(row[1])
        create_pairs(words, syllables, word_syllables)
        lessons.append({
            'phrase': phrase,
            'words': words,
            'word_syllables': word_syllables,
            'all_syllables' : syllables,
            'nodes': nodes,
            'edges': edges
        })
    
    for lesson in lessons:
        if len(lesson['all_syllables']) <= 5:
            easy.append(lesson)
        elif len(lesson['all_syllables']) == 6:
            medium.append(lesson)
        elif len(lesson['all_syllables']) >= 7:
            hard.append(lesson)

    return [easy, medium, hard]


def get_lessons2(type):
    easy_lessons, medium_lessons, hard_lessons = weight.get_difficulties()
    easy_lessons = aux_getlessons2(easy_lessons, type)
    medium_lessons = aux_getlessons2(medium_lessons, type)
    hard_lessons = aux_getlessons2(hard_lessons, type)
    return [easy_lessons, medium_lessons, hard_lessons]

    
def aux_getlessons2(lessons, type):
    lessons_dict = []
    for lesson in lessons:
        word_syllables = {}
        words = []
        syllables = []
        e = pgf.readExpr(lesson[0])
        phrase = zul.linearize(e)
        syllables = convert_expr_to_string_syllables(e)
        nodes = []
        edges = []
        get_AST(e, nodes, edges, an.depth(e), 0, 0, 0, 0, type)
        words = get_words(lesson[1])
        
        create_pairs(words, syllables, word_syllables)
        if type =='builder':
            lessons_dict.append({
                'phrase': phrase,
                'nodes': nodes,
                'edges': edges
            })
        else:
            lessons_dict.append({
                'phrase': phrase,
                'words': words,
                'word_syllables': word_syllables,
                'all_syllables' : syllables,
                'nodes': nodes,
                'edges': edges
            })

    return lessons_dict



