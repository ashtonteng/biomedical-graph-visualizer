import argparse
import json
import numpy as np
import os
import torch
from gensim.models import keyedvectors


def dump_emb_to_json(emb, name2id, outdir, fname, name):
    fpath = os.path.join(outdir, fname)
    print("{} embeddings shape: {}".format(name, emb.shape))
    print("Entities in entity2id: {}".format(len(name2id)))
    emb_dict = {k: emb[int(v)].tolist() for k, v in name2id.items()}
    with open(fpath, 'w') as fp:
        json.dump(emb_dict, fp)
    print("Saved {}".format(fpath))


def _load_tsv_to_dict(fpath):
    res = dict()
    with open(fpath) as f:
        for line in f:
            (k, v) = line.split()
            res[k] = v
    return res


def _load_tsv_to_np(fpath):
    data = np.genfromtxt(fname=fpath, delimiter="\t", skip_header=1)
    return data


def _load_relation_embs(fpath, data_dir):
    model = torch.load(fpath, map_location=torch.device('cpu'))
    eemb = model['final_entity_embeddings'].numpy()
    remb = model['final_relation_embeddings'].numpy()
    return eemb, remb


def _load_stranse_embs(data_dir):
    epath = os.path.join(data_dir, 'entity2vec.txt')
    rpath = os.path.join(data_dir, 'relation2vec.txt')
    eemb = _load_tsv_to_np(epath)
    remb = _load_tsv_to_np(rpath)
    return eemb, remb


def _load_node2vec_embs(data_dir):
    fpath = os.path.join(data_dir, 'embeddings.emb')
    model = keyedvectors.KeyedVectors.load_word2vec_format(fpath)
    vocab = model.wv.index2word
    emb = model.wv.vectors
    e2id = dict()
    for i, w in enumerate(vocab):
        e2id[w] = i
    dump_emb_to_json(emb, e2id, args.data_dir, "ent_emb.json", name='entity')
    exit()


def run(args):
    if args.alg == 'relation':
        eemb, remb = _load_relation_embs(args.emb, args.data_dir)
    elif args.alg == 'stranse':
        eemb, remb = _load_stranse_embs(args.data_dir)
    elif args.alg == 'node2vec':
        eemb, remb = _load_node2vec_embs(args.data_dir)
    else:
        print("Invalid alg chosen. Choices: 'stranse', 'node2vec', 'relation'")
        return
    epath = os.path.join(args.data_dir, 'entity2id.txt')
    rpath = os.path.join(args.data_dir, 'relation2id.txt')
    e2id = _load_tsv_to_dict(epath)
    r2id = _load_tsv_to_dict(rpath)
    dump_emb_to_json(eemb, e2id, args.data_dir, "ent_emb.json", name='entity')
    dump_emb_to_json(remb, r2id, args.data_dir, "rel_emb.json", name='relation')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--alg", type=str, default='relation',
        help="Algorithm used to create embeddings")
    parser.add_argument(
        "--emb", type=str,
        default='/data4/blanca/checkpoints/wikidata-bmi/out200/conv/trained_99.pth',
        help="Embeddings file as .pth")
    parser.add_argument(
        "--data_dir", type=str,
        default='/data4/blanca/data/wikidata-bmi/',
        help="Path where .txt files are saved")
    args = parser.parse_args()
    print(args)
    run(args)

