import pgf, csv
import pgfaux.analyze as an
import pgfaux.generate as gen
import pgfaux.exceptions as exceptions
import numpy as np
import random
import configparser

# Load the PGF file
config = configparser.ConfigParser()
config.read('Config.ini')
gr = pgf.readPGF(config.get('PGF_Config', 'grammar'))
zul = gr.languages[(config.get('PGF_Config', 'conc_syntax'))]
clauses = config.get('PGF_Config', 'clauses_in_syntax')
present_tense = config.get('PGF_Config', 'present_tense')

def calculate_branching_factor(node):
    def helper(node):
        if isinstance(node, pgf.Expr):
            children = node.unpack()[1]
            if not children:
                return (0, 0)  # (sum of branching factors, number of nodes)
            else:
                child_results = [helper(child) for child in children]
                sum_branching = len(children) + sum(result[0] for result in child_results)
                num_nodes = 1 + sum(result[1] for result in child_results)
                return (sum_branching, num_nodes)
        return (0, 0)

    sum_branching, num_nodes = helper(node)
    return sum_branching / num_nodes if num_nodes > 0 else 0

def calculate_nr_nodes(node):
    if isinstance(node, pgf.Expr):  # If the node is an expression
        children = node.unpack()[1]
        if not children:
            return 1  # Leaf node, count itself
        else:
            # Count current node + sum of nodes in children
            return 1 + sum(calculate_nr_nodes(child) for child in children)
    return 1  # Leaf node or non-expression, count itself

def count_clauses(node):
    if isinstance(node, pgf.Expr):  
        fun = node.unpack()[0]
        if fun in clauses: 
            return 1 + sum(count_clauses(child) for child in node.unpack()[1])
        else:
            return sum(count_clauses(child) for child in node.unpack()[1])
    return 0 

def is_present(node):
   node = str(node)
   if present_tense in node :
        return True
   else:
       return False


def calculate_weighted_score(node):
    # Example usage
    branching_factor = calculate_branching_factor(node)
    num_clauses = count_clauses(node) * 100
    tense = is_present(node) * -100
    nr_nodes = calculate_nr_nodes(node)
    tree_depth = an.depth(node)
    score = branching_factor * 100 + num_clauses * 1.6 + tense * 1.5 + nr_nodes *200 + tree_depth *200 
    return score

def section_trees(file):
    file = open(file)
    csv_reader = csv.reader(file)
    header = []
    header = next(csv_reader) 
    parse_trees = []
    for row in csv_reader:
        parse_trees.append(row)
    file.close()

    tree_scores = []
    individual_Scores = []
    total_score = 0
    # avg_score = 0
    # nr_trees = len(parse_trees)
    for parse_tree in parse_trees:
        expr = pgf.readExpr(parse_tree[0])
        score = calculate_weighted_score(expr)
        tree_scores.append([score, parse_tree[0], parse_tree[1]])
        individual_Scores.append(score)
        total_score += score  
    
    # avg_score = total_score/nr_trees
    # print(f'Average Score: {avg_score}')

    elements_count = {}
    # iterating over the elements for frequency
    for element in tree_scores:
    # checking whether it is in the dict or not
        if element[0] in elements_count:
        # incerementing the count by 1
            elements_count[element[0]] += 1
        else:
        # setting the count to 1
            elements_count[element[0]] = 1
    # printing the elements frequencies
    # for key, value in elements_count.items():
    #     print(f"{key}: {value}")

    easy = []
    medium = []
    hard = []

    individual_Scores.sort()
    percentile_25 = np.percentile(individual_Scores, 25)  #25th percentile
    percentile_50 = np.percentile(individual_Scores, 75)  #75th percentile

    thresholds = {
        'easy': percentile_25,
        'medium': percentile_50,
    }

    # print("Easy Thresholds:", thresholds['easy'])
    # print("Medium Thresholds:", thresholds['medium'])

    for element in tree_scores:
        if element[0] <= thresholds['easy']:
            easy.append(element)
        elif element[0] <= thresholds['medium']:
            medium.append(element)
        else:
            hard.append(element)
            
    # print(len(easy))
    # print(len(medium))
    # print(len(hard))
    # print("Modified values: ")

    for easy_tree in easy:
        if elements_count[easy_tree[0]] >= 5:
            easy.remove(easy_tree)
        
    for easy_tree in medium:
        if elements_count[easy_tree[0]] >= 5:
            medium.remove(easy_tree)

    for easy_tree in hard:
        if elements_count[easy_tree[0]] >= 5:
            hard.remove(easy_tree)

    # print(len(easy))
    # print(len(medium))
    # print(len(hard))

    # for easy_tree in easy:
    #     print(zul.linearize(pgf.readExpr(easy_tree[1])))
    return [easy, medium, hard]


def column(matrix, i, word):
    return [[row[i], row[word]] for row in matrix]


#Randomly sample values from the given array of trees
def randomize_array(arr, size):
    random_elements = random.sample(arr, size)
    return random_elements


#get the different trees for a given difficulty
def get_difficulties(difficulty):
    difficultys = section_trees(config.get('PGF_Config', 'treebank'))
    if (difficulty == 'easy'):
        easy = column(difficultys[0], 1, 2)
        easy = randomize_array(easy,10)
        return easy
    elif (difficulty =='medium'):
        medium = column(difficultys[1], 1, 2)
        medium = randomize_array(medium,10)
        return medium
    else:
        hard = column(difficultys[2], 1, 2)
        hard = randomize_array(hard,10)
        return hard
