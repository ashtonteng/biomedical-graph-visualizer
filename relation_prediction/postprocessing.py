import argparse
import os
import torch
import json


def dump_emb_to_json(emb, name2id, outdir, fname, name):
    fpath = os.path.join(outdir, fname)
    print("{} embeddings shape: {}".format(name, emb.shape))
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


def run(args):
    model = torch.load(args.emb, map_location=torch.device('cpu'))
    eemb = model['final_entity_embeddings'].numpy()
    remb = model['final_relation_embeddings'].numpy()
    epath = os.path.join(args.data_dir, 'entity2id.txt')
    rpath = os.path.join(args.data_dir, 'relation2id.txt')
    e2id = _load_tsv_to_dict(epath)
    r2id = _load_tsv_to_dict(rpath)
    dump_emb_to_json(
        eemb, e2id, args.data_dir, "ent_emb.json", name='entity')
    dump_emb_to_json(
        remb, r2id, args.data_dir, "rel_emb.json", name='relation')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
