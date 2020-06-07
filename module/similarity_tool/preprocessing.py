import argparse
import os
import random
import networkx as nx
import numpy as np


def _gen_relation2id(G, outdir):
    outpath = os.path.join(outdir, 'relation2id.txt')
    relations = set()
    edges = G.edges()
    print('{} edges in G'.format(len(edges)))
    for e in edges:
        for k, v in G.get_edge_data(*e).items():
            relations.add(v)
    relation2id = dict()
    rid = 0
    for r in relations:
        relation2id[r] = rid
        rid += 1
    print('{} relations in G'.format(len(relation2id)))
    print('Writing relation2id to {}'.format(outpath))
    f = open(outpath, 'w')
    for k, v in relation2id.items():
        f.write("{}\t{}\n".format(k, v))
    print('Done writing relation2id to {}'.format(outpath))
    f.close()


def _gen_entity2id(nodes, outdir):
    outpath = os.path.join(outdir, 'entity2id.txt')
    print('{} nodes in G'.format(len(nodes)))
    entity2id = dict()
    eid = 0
    for e in nodes:
        entity2id[e] = eid
        eid += 1
    assert len(nodes) == len(entity2id)
    print('Writing entity2id to {}'.format(outpath))
    f = open(outpath, 'w')
    for k, v in entity2id.items():
        f.write("{}\t{}\n".format(k, v))
    print('Done writing entity2id to {}'.format(outpath))
    f.close()


def _write_to_file(path, data):
    f = open(path, 'w')
    for x in data:
        f.write(x)
    f.close()
    print('Done writing data to {}'.format(path))


def _gen_datasplits(G, outdir, trainprop=.8):
    trainpath = os.path.join(outdir, 'train.txt')
    validpath = os.path.join(outdir, 'valid.txt')
    testpath = os.path.join(outdir, 'test.txt')

    examples = list()
    for e in G.edges():
        for k, v in G.get_edge_data(*e).items():
            ex = '{}\t{}\t{}\n'.format(e[0], v, e[1])
            examples.append(ex)

    random.shuffle(examples)
    valprop = (1.-trainprop)/2.
    train, valid, test = np.split(
        examples, [int(
            trainprop * len(examples)), int((1. - valprop) * len(examples))])

    _write_to_file(trainpath, train)
    _write_to_file(validpath, valid)
    _write_to_file(testpath, test)


def preprocess_graph_for_relation_prediction(G, outdir):
    """Create .txt files for relation prediction from networkx graph G.

    file outputs:
        entity2id.txt:
            mapping of entity names to the id. id starts from 0
        relation2id.txt:
            mapping of relation names to the id. id starts from 0
        train.txt, valid.txt, test.txt:
            list of triples in the format entity1 relation entity2

    Args:
        G (Networkx MultiDiGraph):
            Graph to preprocess for STransE and relationPrediction
        outdir (str): Path to output directory
    """
    nodes = G.nodes()
    _gen_relation2id(G, outdir)
    _gen_entity2id(nodes, outdir)
    _gen_datasplits(G, outdir)


def run(args):
    G = nx.read_gpickle(args.pkl)
    preprocess_graph_for_relation_prediction(G, args.outdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pkl", type=str,
        default='/home/blanca/biomedical-graph-visualizer/module/queries/BGV_Graph.pkl',
        help="Path where gpickle is saved")
    parser.add_argument(
        "--outdir", type=str,
        default='/data4/blanca/data/wikidata-bmi/',
        help="Path where .txt files are saved")
    args = parser.parse_args()
    print(args)
    run(args)
