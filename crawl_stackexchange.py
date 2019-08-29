import os
import urllib.request
import random
import requests
import shutil
import xml.etree.ElementTree as ET
import csv
from bs4 import BeautifulSoup

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def contain_non_ascii(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return True
    else:
        return False

# Get 7z Files Download Links
download_links = []
r = requests.get(url = 'https://archive.org/details/stackexchange')
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.findAll('a', {'class': 'stealth download-pill'}):
    href_link = a['href']
    if href_link.endswith('stackexchange.com.7z') and not href_link.endswith('meta.stackexchange.com.7z'):
        download_links.append('https://archive.org' + href_link)

# Download Files
categories = []
create_dir_if_not_exists('raw_data')
for download_link in download_links:
    category_name = download_link[download_link.rfind('/')+1:download_link.rfind('.stackexchange.com.7z')]
    if not os.path.isfile('raw_data/{}.7z'.format(category_name)):
        urllib.request.urlretrieve(download_link, 'raw_data/{}.7z'.format(category_name))
        print('Downloaded {}.7z'.format(category_name))
    else:
        print('File {}.7z already existed'.format(category_name))
    categories.append(category_name)

# Exclude topics:
# + a) that contain a lot of words/sentences that are not in English
# + b) meta.*.csv
# + c) Too many code
categories.remove('latin')
categories.remove('ukrainian')
categories.remove('german')
categories.remove('japanese')
categories.remove('korean')
categories.remove('meta.ukrainian')
categories.remove('meta.vegetarianism')
categories.remove('spanish')
categories.remove('russian')
categories.remove('chinese')
categories.remove('italian')
categories.remove('french')
categories.remove('rus')
categories.remove('math') # Contain too many equations and maybe too little NLP info
categories.remove('portuguese')
categories.remove('tex')
categories.remove('unix')

# Processing
print('')
create_dir_if_not_exists('processed_data/')
create_dir_if_not_exists('temp_data')
for category_name in categories:
    print('Processing {}'.format(category_name))
    shutil.rmtree('temp_data')
    create_dir_if_not_exists('temp_data')

    # Unzip
    os.system('7z x raw_data/{}.7z -oc:temp_data/ > temp_data/7z_log.txt'.format(category_name))

    # Read XML file
    id2post = {}
    questions, answers, answer_ids = [], [], []
    question2relevants = {}
    tree = ET.parse('temp_data/Posts.xml')
    root = tree.getroot()
    for item in root.findall('row'):
        post_id = item.attrib['Id'].strip()
        body_text = BeautifulSoup(item.attrib['Body'], "lxml").text.replace('\n', ' ')
        post_type_id = int(item.attrib['PostTypeId'].strip())
        score = int(item.attrib['Score'])
        if 'http' in body_text or 'html' in body_text: continue
        if contain_non_ascii(body_text): continue
        if post_type_id == 1: # Question
            title = BeautifulSoup(item.attrib['Title'], "lxml").text.replace('\n', ' ')
            questions.append((post_id, title, score))
            id2post[post_id] = questions[-1]
        elif post_type_id == 2 and score > 1 and len(body_text.split(' ')) < 256: # Answer
            answers.append((post_id, body_text, score))
            id2post[post_id] = answers[-1]
            parent_id = item.attrib['ParentId'].strip()
            if not parent_id in question2relevants:
                question2relevants[parent_id] = []
            question2relevants[parent_id].append(post_id)
            answer_ids.append(post_id)

    #
    negative_examples, positive_examples = 0, 0
    data = []
    for post_id, title, score in questions:
        qid = '{}_{}'.format(category_name, post_id)
        question_text = title.strip()
        if not question_text.endswith('?'):
            continue
        len_question_text = len(question_text.split(' '))

        if post_id in question2relevants:
            for answer_id in question2relevants[post_id]:
                cid = '{}_{}_{}'.format(category_name, post_id, answer_id)
                answer_text = id2post[answer_id][1].strip()
                len_answer_text = len(answer_text.split(' '))
                if len_question_text + len_answer_text <= 512:
                    data.append((qid, question_text, cid, answer_text, 1))
                    positive_examples += 1

                # Sample a negative example
                while True:
                    negative_answer_id = random.choice(answer_ids)
                    if not negative_answer_id in question2relevants[post_id] and negative_answer_id in id2post:
                        break
                cid = '{}_{}_{}'.format(category_name, post_id, negative_answer_id)
                candidate_text = id2post[negative_answer_id][1].strip()
                len_answer_text = len(candidate_text.split(' '))
                if len_question_text + len_answer_text <= 512:
                    data.append((qid, question_text, cid, candidate_text, 0))
                    negative_examples += 1

    random.shuffle(data)
    with open('processed_data/{}.csv'.format(category_name), 'w+') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(data)
    print('{} has {} negative examples and {} positive_examples'.format(category_name, negative_examples, positive_examples))
