import os
from glob import glob
import json
from tqdm import tqdm
import subprocess

def wc_count(file_name):
    out = subprocess.getoutput("wc -l %s" % file_name)
    return int(out.split()[0])

with open('done','r') as fr:
    done_list=[line.strip() for line in fr.readlines()]

with open('/home4T_0/jiajq_data/p31_list.txt','r') as fr: 
    p31_list=[line.strip() for line in fr.readlines()]

langs=[i.split('/')[-1] for i in glob('/home4T_0/jiajq_data/gazetteer_v4/ori_data/*')] 

for json_file in tqdm(glob('/home/jiajq/wiki_data/10G.json.*'),desc='total processing'):
    if json_file in done_list:
        print('skip',json_file)
        continue
    #    print(json_file)
    lang2p31list={i:{p31:[] for p31 in p31_list } for i in langs}
    with open(json_file,'r',encoding='utf-8') as fr:
        for line in tqdm(fr,total=1000000,desc='current json processing'):
            if line.startswith('['):
                continue
            try:
                item=json.loads(line[:-2])
            except json.decoder.JSONDecodeError:
                with open('error','a',encoding='utf-8') as fw:
                    fw.write('json.decoder.JSONDecodeError\n'+json_file+'\n'+line+'\n')
                continue

            if 'P31' in item['claims']:
                for p31_item in item['claims']['P31']:
                    if 'datavalue' not in p31_item['mainsnak']:
                        continue
                    p31_id=p31_item['mainsnak']['datavalue']['value']['id']
                    if p31_id in p31_list:
                        for lang in langs: 
                            if lang in item['labels']: 
                                lang2p31list[lang][p31_id].append(item['labels'][lang]['value'])


    for lang, p31_list in lang2p31list.items():  
        for p31_id in p31_list:
            if p31_list[p31_id]==[]:
                continue
            p31_file='/home4T_0/jiajq_data/gazetteer_v5/{}/{}.txt'.format(lang,p31_id) 
            with open(p31_file,'a',encoding='utf-8') as fw:  
                p31_list[p31_id].append('')     
                fw.write('\n'.join(p31_list[p31_id]))    
    with open('done','a') as fw:
        fw.write(json_file+'\n')
