#!/usr/bin/env python3
import sys
import json
import statistics
from lxml import html
from random import shuffle
import requests
from requests.auth import HTTPBasicAuth




def get_Kiper(correct_order,id_name,year=2018):
    with open('Kiper{}'.format(str(year)),'r') as file:
        stuff = '\n'.join(list(file))
        tree = html.fromstring(stuff)
        s = tree.xpath('//h2//text()')
        s1 = tree.xpath('//p//text()')
        picks1_25 = [(x.strip(),s[i+1],s[i+2]) for i, x in enumerate(s) if x[-2:] == '. ' and len(x.strip()) < 5]
        picks26_300 = [(x.strip(),s1[i+1],s1[i+2]) for i, x in enumerate(s1) if x[-2:] == '. ' and len(x.strip()) < 5][:275]
        picks301 = sorted([(int(x.strip()[:-1]),s1[i+1],s1[i+2]) for i, x in enumerate(s1) if x[-2:] == '. ' and len(x.strip()) < 5][275:])
        picks = picks1_25 + picks26_300 + picks301
        names = set([id_name[id] for _,id in correct_order])
        name_id ={}
        for k,v in id_name.items():
            if v in name_id:
                print(v)
                exit(0)
            name_id[v] = k
        big_board = []
        pp = 1
        drafted = set()
        for p, name, _ in picks:
            if clean_name(name) in names and name_id[clean_name(name)] not in drafted:
                drafted.add(name_id[clean_name(name)])
                big_board.append((pp,name_id[clean_name(name)]))
                pp += 1

        names = set([id_name[id] for _,id in big_board])

        for p,id in correct_order:
            if id_name[id] not in names:
                drafted.add(id)
                big_board.append((pp,id))
                pp += 1

    return sorted(big_board)

def clean_name(name):
    name = name.split(' II')[0]
    name = 'r'.join(name.split('\'R'))
    name = 'Chuks'.join(name.split('Chukwuma'))
    name = 'O\'d'.join(name.split('O\'D'))
    name = 'J\'m'.join(name.split('J\'M'))
    name = 'a\'w'.join(name.split('a\'W'))
    name = 'R.J.'.join(name.split('RJ'))
    name = 'Deshon'.join(name.split('DeShon'))
    name = 'JuJu'.join(name.split('Juju'))
    name = 'DeShone'.join(name.split('Deshone'))
    name = 'Mitchell'.join(name.split('Mitch'))
    name = 'Chris Campb'.join(name.split('Christian Campb'))
    name = name.split(' Jr.')[0]
    name = '_'.join(name.split())

    return name

def clean(text,name):
    text = '--NAME--'.join(text.split(name))
    text = '--NAME--'.join(text.split(name.split()[0]))
    text = '--NAME--'.join(text.split(name.split()[-1]))
    text = text.rstrip()
    text = text.split('\n-Nolan')[0]
    text = text.split('\n-Lance')[0]
    text = ' '.join(text.split('...'))
    text = 'Number'.join(text.split('No.'))
    #text = ' '.join(text.split('.'))
    text = ' '.join(text.split('\\r\\n'))
    text = text.split('\nQ & A')[0]
    return text

def recurse(d,name):
    if type(d) == type(""):
        return d
    else:
        text = []
        for key, d2 in sorted(d.items(),reverse=True):
            if key not in ['Related Links','Pro Day Results']:
                field = recurse(d2,name)
                if key == 'Sources Tell Us' and field == 'Weaknesses':
                    continue
                if field:
                    #if key != 'plain_text':
                    #    text.append(key)
                    text.append(clean(field.rstrip(),name))
        text = '\n'.join(text)
        text = clean(text,name)
        return text

def process_data():
    draft = {}
    for i in ['08','09','10','11','12','13','14','15','16','17','18']:
        with open('data'+i+'.json') as file:
            draft.update(json.load(file))

    total = 0
    for year in draft.keys():
        count = 0
        print(year)
        file = open('text_'+year,'w+')
        for player_id in list(draft[year].keys()):
            try:
                draft[year][player_id]['text']['Analysis']
            except:
                continue
            count += 1
            text = recurse(draft[year][player_id]['text'],draft[year][player_id]['name'])
            if count > 1:
                file.write('-'*25+'\n')
            file.write('{} {} {}\n'.format('_'.join(draft[year][player_id]['name'].split()),player_id,str(draft[year][player_id]['pick'])))
            file.write(text+'\n')
        print(count,len(draft[year].keys()))
        total += count
        file.close()
    print('TOTAL',total)

def score(guess_order,player_correct):
    total = 0
    rtotal = 0
    worst = 0
    r = list(range(1,len(guess_order)+1))
    shuffle(r)
    for i, value in enumerate(guess_order):
        id = value[-1]
        c = player_correct[id]
        worst_pick = (len(guess_order)-(2*c-1))*(len(guess_order)-(2*c-1))/c
        worst += worst_pick
        total += (c-i)*(c-i)/c
        rtotal += (c-r[c-1])*(c-r[c-1])/c
    return total/worst, rtotal/worst

def train(devyear=2018,testyear=2017,UNIGRAM=1,BIGRAM=1,curve=0.99995,BONUS=0,MULTIPLY=1,WORD_MULTIPLY=150,ROUND_MULTIPLY=250,MIN_COUNT=5,RANGE=75):
    word_value = {}
    bl = 40
    common_words = set("a an and are as at be by for from has he in is it its of on that the to was were will with".split())
    positive = set(['win','wins','top','ability','speed','skills','productive','excellent','excelled','good','star','big','bigger','biggest','great','above','early','best','strength','strong','fast','faster','fastest','strongest','accurate','high','Pro','Bowl','Bowler'])
    negative = set(['limitation','limitations','lose','loses','average','too','struggle','struggles','struggles','doesn\'t','won\'t','can\'t','bad','lack','not','no','lacks','poor','below','worst','weakness','late','weak','slow','slower','slowest','weakest','inaccurate','inaccuracy','low','bust'])

    key_traits = set()
    if MULTIPLY:
        with open('key_traits-{}-{}'.format(str(MIN_COUNT),str(RANGE)),'r+') as keys:
            for line in keys:
                key_traits.add(line.split(', ')[1])
    years = set(range(2008,2019))
    years.remove(devyear)
    years.remove(testyear)
    years = list(years)
    count = 0
    for year in years:
        print('Training: |{}{}|\r'.format('▓'*int(bl*count/len(years)/(UNIGRAM+BIGRAM)),'_'*(bl-int(bl*count/len(years)/(UNIGRAM+BIGRAM)))),end='')
        text = ""
        with open('text_'+str(year)) as file:
            for line in file:
                text += line
        text = text.split('-'*25)
        if UNIGRAM:
            for section in text:
                section = section.lstrip()
                try:
                    name, id, pick = section.split('\n')[0].split()
                except:
                    print(year)
                    exit(0)
                body = section.split('\n',1)[-1].split()
                for i in range(len(body)-1):

                    s = body[i].rstrip().lower()
                    s = ''.join(s.split('('))
                    s = ''.join(s.split(')'))
                    s = ''.join(s.split('.'))
                    s = ''.join(s.split(','))

                    if (BONUS or MULTIPLY) and s in common_words or s == '':
                        continue


                    multiplier = 1
                    if MULTIPLY and s in key_traits:
                         multiplier = WORD_MULTIPLY

                    good = -20
                    bad = 20
                    bonus = 0
                    bonus = int(s in positive)*good + int(s in negative)*bad

                    if not BONUS:
                        bonus = 0

                    if s not in word_value:
                        word_value[s] = ([float(pick)*multiplier+bonus],1*multiplier,float(pick)*multiplier+bonus)
                    else:
                        total,times,avg = word_value[s]
                        total.append(float(pick)*multiplier+bonus)
                        times += multiplier
                        avg = sum(total)/times
                        word_value[s] = (total,times,avg)
            count += 1
        if BIGRAM:
            for section in text:
                section = section.lstrip()
                try:
                    name, id, pick = section.split('\n')[0].split()
                except:
                    print(year)
                    exit(0)
                body = section.split('\n',1)[-1].split()
                for i in range(len(body)-1):
                    s1 = body[i].rstrip().lower()
                    s2 = body[i+1].rstrip().lower()
                    if '.' in s1:
                         continue
                    s = s1+' '+s2
                    s = ''.join(s.split('('))
                    s = ''.join(s.split(')'))
                    s = ''.join(s.split('.'))
                    s = ''.join(s.split(','))

                    multiplier  = 1
                    if MULTIPLY and s in key_traits:
                         multiplier = WORD_MULTIPLY
                    good = -20
                    bad = 20
                    bonus = 0
                    bonus = int(s1 in positive)*good + int(s1 in negative)*bad + int(s2 in positive)*good + int(s2 in negative)*bad

                    if not BONUS:
                        bonus = 0
                    if MULTIPLY and 'round' in s and ('1' in s or '2' in s or '3' in s or '4' in s or '5' in s or '6' in s or '7' in s):
                        s = 'round'.join(s.split('rounds'))
                        multiplier = 250
                    if s not in word_value:
                        word_value[s] = ([float(pick)*multiplier+bonus],1*multiplier,float(pick)*multiplier+bonus)
                    else:
                        total,times,avg = word_value[s]
                        total.append(float(pick)*multiplier+bonus)
                        times += multiplier
                        avg = sum(total)/times
                        word_value[s] = (total,times,avg)
            count += 1
    return word_value

def test_model(word_value,testyear=2018,UNIGRAM=1,BIGRAM=1,curve=0.99995,BONUS=0,MULTIPLY=1,WORD_MULTIPLY=150,ROUND_MULTIPLY=250,MIN_COUNT=5,RANGE=75):
    player_guess = {}
    player_correct = {}
    id_name = {}
    year = testyear
    text = ""
    with open('text_'+str(year)) as file:
        for line in file:
            text += line
    text = text.split('-'*25)
    if UNIGRAM:
        for section in text:
            section = section.lstrip()
            name, id, pick = section.split('\n')[0].split()
            id_name[id] = name
            player_correct[id] = int(pick)
            body = section.split('\n',1)[-1].split()
            for i in range(len(body)):
                s = body[i].rstrip().lower()
                if s not in word_value:
                    continue
                else:
                    if id not in player_guess:
                        player_guess[id] = (0,0,0)
                    total,times,avg = player_guess[id]
                    stotal,stimes,savg = word_value[s]
                    if stimes > 0:
                        total += sum(stotal)
                        times += stimes
                        avg = total/times
                        player_guess[id] = (total*curve,times,avg)
    if BIGRAM:
        for section in text:
            section = section.lstrip()
            name, id, pick = section.split('\n')[0].split()
            id_name[id] = name
            player_correct[id] = int(pick)
            body = section.split('\n',1)[-1].split()
            for i in range(len(body)-1):
                s1 = body[i].rstrip().lower()
                s2 = body[i+1].rstrip().lower()
                s = s1+' '+s2
                if 'round' in s and ('1' in s or '2' in s or '3' in s or '4' in s or '5' in s or '6' in s or '7' in s):
                    s = 'round'.join(s.split('rounds'))
                if s not in word_value:
                    continue
                else:
                    if id not in player_guess:
                        player_guess[id] = (0,0,0)
                    total,times,avg = player_guess[id]
                    stotal,stimes,savg = word_value[s]
                    if stimes > 0:
                        total += sum(stotal)
                        times += stimes
                        avg = total/times
                        player_guess[id] = (total*curve,times,avg)

                    else:
                        player_guess[id] = (word_value[s][-1],1,word_value[s][-1])
    guess_order = sorted([(value[-1],id) for id,value in player_guess.items()])
    correct_order = sorted([(pick,id) for id,pick in player_correct.items()])
    for i in range(len(correct_order)):
        player_correct[correct_order[i][-1]] = i+1
        correct_order[i] = (i+1,correct_order[i][-1])
    # n = sorted([(v[-1],k,[min(v[0]),sum(v[0])/len(v[0]),max(v[0]),len(v[0])]) for k,v in word_value.items() if len(v[0]) > 3])
    # with open('key_traits-4-50','w+') as keys:
    #     [keys.write(', '.join([str(kk) for kk in x])+'\n') for x in n if x[-1][2] - x[-1][0] < 50 and x[1].split()[0] not in common_words and x[1].split()[-1] not in common_words]
    # with open('key_traits-4-75','w+') as keys:
    #     [keys.write(', '.join([str(kk) for kk in x])+'\n') for x in n if x[-1][2] - x[-1][0] < 75 and x[1].split()[0] not in common_words and x[1].split()[-1] not in common_words]
    # with open('key_traits-4-25','w+') as keys:
    #     [keys.write(', '.join([str(kk) for kk in x])+'\n') for x in n if x[-1][2] - x[-1][0] < 25 and x[1].split()[0] not in common_words and x[1].split()[-1] not in common_words]

    # with open('bad_traits','w+') as bad:
    #     [bad.write(', '.join([str(kk) for kk in x])+'\n') for x in sorted(n[-300:],reverse=True)]
    # word1 = 'ray guy'
    # word2 = 'strength'
    # word3 = 'herschel walker'
    # print(word1,min(word_value[word1][0]),max(word_value[word1][0]),word_value[word1][1],word_value[word1][-1])
    # print(word2,min(word_value[word2][0]),max(word_value[word2][0]),word_value[word2][1],word_value[word2][-1])
    # print(word3,min(word_value[word3][0]),max(word_value[word3][0]),word_value[word3][1],word_value[word3][-1])
    return (guess_order,correct_order,id_name,player_correct)


def print_results(guess_order,correct_order,id_name,player_correct):

    space = 25
    heading = '|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|'.format('PICK','CORRECT_PLAYER','DRAFTED','GUESS_PLAYER','DRAFTED','GUESS_SCORE',space=space)
    print(heading)
    print('-'*len(heading))

    for i in range(len(guess_order)):
        row = '|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|{:<{space}}|'.format(i+1,id_name[correct_order[i][-1]],correct_order[i][0],id_name[guess_order[i][-1]],player_correct[guess_order[i][-1]],guess_order[i][0],space=space)
        print(row)

def usage(status=0):
    print(
    '''USAGE:
    BY DEFUALT THE MODEL RUNS THE OPTIMAL PARAMETERS FOR THE DEVELOPMENTS SET
    -t runs the model on the test dataset as opposed to the development dataset
    -b [1,2,3,4]  Baseline Models
        1: run the SIMPLE model
        2: run the BASIC-CONTEXT model
        3: run the BAG-OF-BIGRAMS model
        4: run the REWARD LONGER EVALUATION model with curve of 0.99995
    -w [INTEGER] word multiply weight (default 150)
    -p [INTEGER] projection multiply weight (default 250)
    -c [FLOAT] Longer Evaluation curve (0-1, default 0.99995)
    -m [INTEGER] minimum count (default 5)
    -r [INTEGER] maximum range (default 75)
    ''')
    exit(status)

def main():


    UNIGRAM = 1
    BIGRAM = 1
    CURVE = 0.99995
    BONUS = 0
    MULTIPLY = 1
    WORD_MULTIPLY = 150
    ROUND_MULTIPLY = 250
    RANGE = 75
    MIN_COUNT = 5
    TEST = 0
    b = -1

    args = sys.argv[1:]
    while len(args) > 0:
        arg = args.pop(0)
        if arg == '-b' and len(args) > 0:
            try:
                b = int(args.pop(0))
                continue
            except:
                usage(1)
        if arg == '-c' and len(args) > 0:
            try:
                CURVE = float(args.pop(0))
                continue
            except:
                usage(1)
        if arg == '-w' and len(args) > 0:
            try:
                WORD_MULTIPLY = int(args.pop(0))
                continue
            except:
                usage(1)
        if arg == '-p' and len(args) > 0:
            try:
                ROUND_MULTIPLY = int(args.pop(0))
                continue
            except:
                usage(1)
        if arg == '-m' and len(args) > 0:
            try:
                MIN_COUNT = int(args.pop(0))
                if MIN_COUNT not in [4,5,6]:
                    usage(1)
                continue
            except:
                usage(1)
        if arg == '-r' and len(args) > 0:
            try:
                RANGE = int(args.pop(0))
                if RANGE not in [25,50,75]:
                    usage(1)
                continue
            except:
                usage(1)
        if arg == '-t':
            TEST = 1
            continue
        usage(0)

    if b == 1:
        UNIGRAM = 1
        BIGRAM = 0
        CURVE = 1
        BONUS = 0
        MULTIPLY = 0
    if b == 2:
        UNIGRAM = 1
        BIGRAM = 0
        CURVE = 1
        BONUS = 1
        MULTIPLY = 0
    if b == 3:
        UNIGRAM = 0
        BIGRAM = 1
        CURVE = 1
        BONUS = 0
        MULTIPLY = 0
    if b == 4:
        UNIGRAM = 1
        BIGRAM = 0
        CURVE = 0.99995
        BONUS = 0
        MULTIPLY = 0




    #process_data()
    devyear = 2018-TEST
    testyear = 2017+TEST
    model = train(devyear,testyear,UNIGRAM,BIGRAM,CURVE,BONUS,MULTIPLY,WORD_MULTIPLY,ROUND_MULTIPLY,MIN_COUNT,RANGE)
    guess_order,correct_order,id_name,player_correct = test_model(model,devyear,UNIGRAM,BIGRAM,CURVE,BONUS,MULTIPLY,WORD_MULTIPLY,ROUND_MULTIPLY,MIN_COUNT,RANGE)
    kiper_order = get_Kiper(correct_order,id_name,devyear)
    print_results(guess_order,correct_order,id_name,player_correct)
    model_score, random_score = score(guess_order,player_correct)
    kiper_score, random_score = score(kiper_order,player_correct)
    print('Model Score: {}\nRandom Model Score: {}\nMel Kiper Jr. Score: {}'.format(model_score,random_score,kiper_score))



if __name__ == '__main__':
    main()
