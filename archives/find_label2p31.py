from utils import *
import pickle
import re
import codecs
import json
from glob import glob
from tqdm import tqdm

def load_link2label(fpath):
    link2label={}
    for fname in glob(f'{fpath}/*/*.txt'):
        label=fname.split('/')[-1].split('.')[0]
        for line in  codecs.open(fname,'r','utf-8'):
            line=line.strip().split(' ||| ')
            for link in line[1:]:
                if link in link2label and label!=link2label[link]:
                    link2label.pop(link)
                    continue
                link2label[link]=label
    
    return link2label
  

link2label=load_link2label('./semeval_ent2href')
label2p31={label:list() for label in ENT_LABELS}
link2p31={}
for fname in tqdm(glob('./wiki_data_needed_info/10G.json.*')):
    with open(fname,'r',encoding='utf-8') as fin:
        json_data=json.load(fin)
    for item_id, data in json_data.items():
        for lang,lang_title in data['wikititle'].items():
            lang_title=lang_title.lower()
            if lang_title in link2label:
                label2p31[link2label[lang_title]].extend(data['P31'])
                if lang_title not in link2p31:
                    link2p31[lang_title]=set()
                link2p31[lang_title].update(data['P31'])
                continue

temp_lines=[]
with open('./wiki_link2p31.txt','w',encoding='utf-8') as fw:

    for link,p31_list in link2p31.items():
        fw.write('{} ||| {}\n'.format(link,' ||| '.join(p31_list)))

for label, p31_list in label2p31.items():
    write_lines(f'./wiki_matched_label2p31/{label}.txt',p31_list)


