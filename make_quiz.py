# LGPL2
# Donut made this

import csv
import json
import os

import argparse
from sudachipy import tokenizer
from sudachipy import dictionary

# kana convert
hira_start = int("3041", 16)
hira_end = int("3096", 16)
kata_start = int("30a1", 16)

hira_to_kata = dict()
kata_to_hira = dict()
for i in range(hira_start, hira_end+1):
    hira_to_kata[chr(i)] = chr(i-hira_start+kata_start)
    kata_to_hira[chr(i-hira_start+kata_start)] = chr(i)

def katakana_to_hiragana(text):
    result = ''
    for c in text:
        result += kata_to_hira[c]
    return result

# dictionaries
bilingual_dict = {}
def get_bilingual_dict():
    if bilingual_dict: return bilingual_dict

    for filename in os.listdir('./jmdict'):
        with open('./jmdict/'+filename, encoding='utf-8') as file:
            jmdict_bank = json.load(file)

            for entry in jmdict_bank:
                term = entry[0]

                if term not in bilingual_dict:
                    bilingual_dict[term] = {'readings':[],'meanings':[]}

                bilingual_dict[term]['readings'].append(entry[1])
                bilingual_dict[term]['meanings'] += entry[5]

    return bilingual_dict

monolingual_dict = {}
def get_monolingual_dict():
    if monolingual_dict: return monolingual_dict

    for filename in os.listdir('./meikyou_kokugo'):
        with open('./meikyou_kokugo/'+filename, encoding='utf-8') as file:
            meikyou_kokugo_bank = json.load(file)

            for entry in meikyou_kokugo_bank:
                term = entry[0]

                if term not in monolingual_dict:
                    monolingual_dict[term] = {'readings':[],'meanings':[]}

                monolingual_dict[term]['readings'].append(entry[1])

                if isinstance(entry[5][0],str):
                    monolingual_dict[term]['meanings'].append(entry[5][0])
                else:
                    monolingual_dict[term]['meanings'].append(entry[5][0]['content'][0])

    return monolingual_dict

# load words
def get_quiz_json(filename):
    with open(filename, encoding='utf-8') as file:
        quiz_bank = json.load(file)

    return quiz_bank['cards']

def get_quiz_csv(filename):
    with open(filename, encoding='utf-8') as file:
        reader = csv.reader(file,delimiter=',')

        return [{'question':row[0], 'answer':row[1], 'meaning':row[2]} for row in reader]

def main():
    # parse args

    parser = argparse.ArgumentParser(description='Make a kotoba quiz')
    parser.add_argument('input',help='Input file')
    parser.add_argument('-o','--outfile',default='./words.json',help='Output file')
    parser.add_argument('-n1',action='store_const',const=True,help='Remove words below n1')
    parser.add_argument('-n2',action='store_const',const=True,help='Remove words below n2')
    parser.add_argument('-n3',action='store_const',const=True,help='Remove words below n3')
    parser.add_argument('-n4',action='store_const',const=True,help='Remove words below n4')
    parser.add_argument('-n5',action='store_const',const=True,help='Remove words below n5')
    parser.add_argument('-e','--exclude',default='./exclude.txt',help='List of words to exclude. 1 word per line.')

    args = parser.parse_args()

    excluded_terms = set()
    with open('excluded.txt', encoding='utf-8') as file:
        excluded_terms = excluded_terms.union(
            (line.split('#')[0]).rstrip()
            for line in file.readlines()
            if (line.split('#')[0]).rstrip()
        )

    if args.n1:
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n1.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n2.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n3.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n4.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n5.csv')))
    elif args.n2:
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n2.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n3.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n4.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n5.csv')))
    elif args.n3:
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n3.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n4.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n5.csv')))
    elif args.n4:
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n4.csv')))
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n5.csv')))
    elif args.n5:
        excluded_terms = excluded_terms.union(set(entry['question'] for entry in get_quiz_csv('./tangorin/jlpt_n5.csv')))

    input_filename = args.input
    output_filename = args.outfile

    # tokenize input
    with open(input_filename, 'r', encoding='utf-8') as file:
        text = file.read()

    tokens = {}

    tokenizer_obj = dictionary.Dictionary(dict_type="full").create()  # sudachidict_full

    for token in tokenizer_obj.tokenize(text):
        if token.part_of_speech()[0] in ['空白','記号','補助記号','助詞','助動詞','連体詞']:
            continue

        dictionary_form = token.dictionary_form()
        if dictionary_form not in get_bilingual_dict():
            continue

        if dictionary_form in excluded_terms:
            continue

        part_of_speech = token.part_of_speech()
        readings = list(set(get_bilingual_dict()[dictionary_form]['readings']))
        meanings = list(set(get_bilingual_dict()[dictionary_form]['meanings']))

        if not readings or readings[0] == '': # eliminates kana only words
            continue

        tokens[token.dictionary_form()] = {
            'dictionary_form': dictionary_form,
            'part_of_speech': part_of_speech,
            'readings': readings,
            'meanings': meanings,
        }


    # create quiz
    cards = []
    for key,token in tokens.items():
        cards.append({
            'question': token['dictionary_form'],
            'answer': token['readings'],
            'meaning': ', '.join(token['meanings'])
        })

    quiz = {'cards':cards}

    with open(output_filename, 'w+', encoding='utf-8') as file:
        json.dump(quiz,file,indent=4,ensure_ascii=False)

if __name__ == "__main__":
    main()
