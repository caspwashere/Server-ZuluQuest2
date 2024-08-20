import pgf
import pgfaux.analyze as an
import csv
import re
import random
import weight
import configparser

# grammar = pgf.readPGF("NguniDev.pgf")
# zul = grammar.languages['DevLangZul']
config = configparser.ConfigParser()
config.read('Config.ini')
grammar = pgf.readPGF(config.get('PGF_Config', 'grammar'))
zul = grammar.languages[(config.get('PGF_Config', 'conc_syntax'))]

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

def get_AST(expr, nodes, edges, max_depth, curr_depth, node_id, offset, parent_node_id, type, subtrees2):

    if curr_depth > max_depth: return
    # print(expr)
    label = an.root_str(expr) + ":" + an.root_cat(expr, grammar)
    if (curr_depth == max_depth):
       if type =='builder':
            functions_by_cat = grammar.functionsByCat(an.root_cat(expr,grammar))
            func = list(filter(lambda x: zul.hasLinearization(x), functions_by_cat))

            nodes.append({
            'id': str(node_id),
            'data': {
                'label': label,
                'list': func,
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
        if type == 'builder':
            functions_by_cat = grammar.functionsByCat(an.root_cat(expr,grammar))
            func = list(filter(lambda x: zul.hasLinearization(x), functions_by_cat))
            nodes.append({
                'id': str(node_id),
                'data': {
                'label': label,
                'list': func,
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
    key_for_subtree = an.root_str(expr) +"_"+str(node_id)
    for child in children:
        offset += 1 + random.randrange(1,10000)
        if key_for_subtree not in subtrees2:
             subtrees2[key_for_subtree] = [an.root_str(child) + ":" + an.root_cat(child, grammar) + "_"+str(node_id + offset)]
        else:
            subtrees2[key_for_subtree].append(an.root_str(child) + ":" + an.root_cat(child, grammar) + "_"+str(node_id + offset))
        
        get_AST(child, nodes, edges, max_depth, curr_depth+1, node_id + offset, offset, node_id, type, subtrees2)


def get_lessons2(type, difficulty):
    lessons = weight.get_difficulties(difficulty)
    lessons = aux_getlessons2(lessons, type, difficulty)
    return lessons

    
def aux_getlessons2(lessons, type, difficulty, hardmode='false'):
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
        subtrees2 = {}
        get_AST(e, nodes, edges, an.depth(e), 0, 0, 0, 0, type, subtrees2)
        words = get_words(lesson[1])
        create_pairs(words, syllables, word_syllables)
        print(subtrees2)
        if type =='builder':
            if hardmode == 'false':
                if difficulty == 'hard':
                    empty_nodes = 4
                else:
                    empty_nodes = 2

                random_numbers = random.sample(range(0, len(nodes)), empty_nodes)
                for number in random_numbers:
                    if nodes[number]['type'] == 'grammar-node':
                        rand_nr = random.randrange(0, len(nodes))
                        if nodes[rand_nr]['type'] != 'grammar-node':
                            nodes[rand_nr]['type'] == 'grammar-node'
                    else:
                        nodes[number]['type'] = 'grammar-node'
                for node in nodes:
                    node['data']['label'] = node['data']['label'] +"_" + node['id']
                lessons_dict.append({
                'phrase': phrase,
                'nodes': nodes,
                'edges': edges
                })
            else:
                #return only root node
                functions_by_cat = grammar.functionsByCat(an.root_cat(e, grammar))
                func = list(filter(lambda x: zul.hasLinearization(x), functions_by_cat))
                startingNode =  an.root_str(e) + ":" + an.root_cat(e, grammar)
                subtrees = {}
                for node in nodes:
                    node['type'] = 'custom-node'
               # print('lesson   ' + str(e))
                get_subtrees(e, an.root_str(e), subtrees)
               # print(subtrees)
                lessons_dict.append({
                'nodes': [{
                                'id': '0',
                                'data': {
                                    'label': startingNode+"_0",
                                    'list': func
                                },
                                'type': 'hardmode-node',
                                'position': {
                                    'x': 0,
                                    'y':0,
                                }
                            }],
                'phrase': phrase,
                'correct-nodes': subtrees,
                'correct-nodes2': subtrees2,
                'solution': [nodes, edges]
                # 'edges': edges
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


def get_hardmode(difficulty):
    lessons = weight.get_difficulties(difficulty)
    lessons = aux_getlessons2(lessons, 'builder', difficulty, 'true')
    return lessons
    

def get_hardmode_node(function_name, node_id, correctNodes):
    function_type = str(grammar.functionType(function_name))
    print(function_type)
    function_children = function_type.split(' -> ')[:-1]
    category = function_type.split(' -> ')[-1]
    nodes = []
    edges = []
    offset = int(node_id)
    correct_children = []
    if function_name +"_"+node_id in correctNodes:
        correct_children = correctNodes[function_name +"_"+node_id]
    index = 0
    print(correct_children)
    for child in function_children:
        list_of_children = grammar.functionsByCat(child)
        list_of_children = list(filter(lambda x: zul.hasLinearization(x), list_of_children))
        label = child +""
        if len(correct_children) > 0:
            offset = correct_children[index].split(':')[1].split('_')[1]
            label = correct_children[index]
        else:
            offset += 1 + random.randrange(1,10000)
            label +=  "_"+ str(offset) 

        index += 1
        print('New label: ' + label)
        nodes.append({
            'id': str(offset),
            'data': {
                'label': label,
                'list': list_of_children,
                'parent': function_name,
                'parentid': node_id,
            },
            'type': 'hardmode-node',
            'position': {
                'x': 250,
                'y': 150,
            }
        })
        edges.append({
            'id': str(node_id)+'-'+str(offset),
            'source': str(node_id),
            'target': str(offset),
            'type': 'custom-edge',
        })
    #print(nodes)
    #print("EDGES #######################")
    #print(edges)
    return [nodes, edges]

def get_subtrees(expr, rootFunc, subtrees):
    #this works as a dict if there are no duplicates...
    subtree = an.children_trees(expr)
    subt = []
    for tree in subtree:
        subt.append(an.root_str(tree) + ":" + an.root_cat(tree, grammar))
        get_subtrees(tree, an.root_str(tree), subtrees )
    subtrees[rootFunc] = subt
