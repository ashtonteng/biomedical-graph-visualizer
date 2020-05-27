import random
import networkx as nx
import numpy as np
import pickle


def _gen_relation2id(edges, outpath='./relation2id.txt'):
    relations = set()
    print('{} edges in G'.format(len(edges)))
    for e in edges:
        for k, v in G.get_edge_data(*e).items():
            relations.add(v['relation_id'])
    relation2id = dict()
    rid = 0
    for r in relations:
        relation2id[r] = rid
        rid += 1
    print('{} relations in G'.format(len(relation2id)))
    print('Writing relation2id to {}'.format(outpath))
    f = open(outpath,'a')
    for k, v in relation2id.items():
        f.write("{}\t{}\n".format(k,v))
    print('Done writing relation2id to {}'.format(outpath))
    f.close()


def _gen_entity2id(nodes, outpath='./entity2id.txt'):
    print('{} nodes in G'.format(len(nodes)))
    entity2id = dict()
    eid = 0
    for e in nodes:
        entity2id[e] = eid
        eid += 1
    print('{} entities in G'.format(len(entity2id)))
    print('Writing entity2id to {}'.format(outpath))
    f = open(outpath,'a')
    for k, v in entity2id.items():
        f.write("{}\t{}\n".format(k,v))
    print('Done writing entity2id to {}'.format(outpath))
    f.close()


def _write_to_file(path, data):
    f = open(path, 'a')
    for x in data:
        f.write(x)
    f.close()
    print('Done writing data to {}'.format(path))


def _gen_datasplits(
    edges, trainprop=.8,
    trainpath='/data4/blanca/data/wikidata-bmi/train.txt',
    validpath='/data4/blanca/data/wikidata-bmi/valid.txt',
    testpath='/data4/blanca/data/wikidata-bmi/test.txt'):
    examples = list()
    for e in edges:
        for k, v in G.get_edge_data(*e).items():
            ex = '{}\t{}\t{}\n'.format(e[0], v['relation_id'], e[1])
            examples.append(ex)

    random.shuffle(examples)
    valprop = (1.-trainprop)/2.
    train, valid, test = np.split(
        examples, [int(trainprop * len(examples)), int((1. - valprop) * len(examples))])

    _write_to_file(trainpath, train)
    _write_to_file(validpath, valid)
    _write_to_file(testpath, test)


def preprocess_graph_for_relation_prediction(
    G=None, path='/data4/blanca/biomedical-graph-visualizer/BGV_Graph.pkl'):
    """Create necessary .txt files for relation prediction from networkx graph G

    inputs:
        G: networkx MultiDiGraph
    file outputs:
        entity2id.txt:
            mapping of entity names to the id. id starts from 0
        relation2id.txt:
            mapping of relation names to the id. id starts from 0
        train.txt, valid.txt, test.txt:
            list of triples in the format entity1 relation entity2
    """
    if G is None:
        G = nx.read_gpickle(path)
    edges = G.edges()
    nodes = G.nodes()
    _gen_relation2id(edges)
    _gen_entity2id(nodes)
    _gen_datasplits(edges)


