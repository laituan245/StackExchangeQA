import os
import csv
import random
from os import listdir
from os.path import isfile, join
from pytorch_pretrained_bert.tokenization import BertTokenizer

PROCESSED_DATA_PATH = 'processed_data'

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Prepare Tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased',
                                          do_lower_case=True,
                                          do_basic_tokenize=True)

all_rows = []
question_ids = set([])
fps = [join(PROCESSED_DATA_PATH, f) for f in listdir(PROCESSED_DATA_PATH) if isfile(join(PROCESSED_DATA_PATH, f)) if f.endswith('.csv')]
for fp in fps:
    with open(fp, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            all_rows.append(row)
            question_ids.add(row[0].strip())
question_ids = list(question_ids)
random.shuffle(question_ids)

train_question_ids = set(question_ids[:-1000])
dev_question_ids = set(question_ids[-1000:-500])
test_question_ids = set(question_ids[-500:])

nb_skipped = 0
nb_passed = 0
train_rows, dev_rows, test_rows = [], [], []
nb_positive_count = {}
for row in all_rows:
    answer_text = row[3].strip()
    if '$' in answer_text or '</' in answer_text or 'sudo' in answer_text or ' rm ' in answer_text or 'foreach' in answer_text \
	or ('[' in answer_text and ']' in answer_text):
        nb_skipped += 1
        continue
    try:
        concat_text = unicode(row[1].strip() + ' ' + row[2].strip())
    except UnicodeDecodeError:
        continue

    if len(tokenizer.tokenize(concat_text.lower())) > 256:
        nb_skipped += 1
        continue
    if row[0].strip() in train_question_ids:
        train_rows.append(row)
    elif row[0].strip() in dev_question_ids:
        dev_rows.append(row)
    elif row[0].strip() in test_question_ids:
        test_rows.append(row)
    if int(row[-1]) == 1:
        nb_positive_count[row[0]] = nb_positive_count.get(row[0], 0) + 1
    nb_passed += 1
    if nb_passed % 10000 == 0:
        print('nb_passed = {}'.format(nb_passed))
random.shuffle(train_rows)
random.shuffle(dev_rows)
random.shuffle(test_rows)

_dev_rows = []
for row in dev_rows:
    if nb_positive_count.get(row[0], 0) > 0:
        _dev_rows.append(row)
dev_rows = _dev_rows

_test_rows = []
for row in test_rows:
    if nb_positive_count.get(row[0], 0) > 0:
        _test_rows.append(row)
test_rows = _test_rows

dev_question_ids = set([row[0] for row in dev_rows])
test_question_ids = set([row[0] for row in test_rows])

print('nb_skipped = {}'.format(nb_skipped))
print('Number of train rows = {} | Number of train questions: {}'.format(len(train_rows), len(train_question_ids)))
print('Number of dev rows = {} | Number of dev questions: {}'.format(len(dev_rows), len(dev_question_ids)))
print('Number of test rows = {} | Number of test questions: {}'.format(len(test_rows), len(test_question_ids)))

create_dir_if_not_exists('final_data')
with open('final_data/train.csv', 'w+') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(train_rows)

with open('final_data/dev.csv', 'w+') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(dev_rows)

with open('final_data/test.csv', 'w+') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(test_rows)
