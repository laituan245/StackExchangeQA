# StackExchangeQA Dataset

## Introduction
This repo has the code for constructing the StackExchangeQA dataset mentioned in the following EMNLP 2019 paper:

`Tuan Lai, Quan Hung Tran, Trung Bui, Daisuke Kihara. A Gated Self-attention Memory Network for Answer Selection. EMNLP 2019`

The paper aims to tackle the answer selection problem. Given a question and a set of candidate answers, the task is to identify which of the candidates answers the question correctly. In addition to proposing a new neural architecture for the task, the paper also proposes a simple but effective transfer learning approach for taking advantage of the large amount of community question answering data available online. More specifically, the paper shows that pre-training an answer selection model on the StackExchangeQA dataset can improve the performance on datasets such as TrecQA and WikiQA.

## To-Do List
To-Do List:
- [ ] Clean up the script files 
- [ ] Add example commands for using the script files

## Note
* The original StackExchangeQA dataset that we collected requires a storage size of more than 2GB. Therefore, we can only distribute the code for constructing the dataset at this time.
* This work was conducted at [Adobe Research](https://research.adobe.com/).
* For any inquiry, please open a Github issue or contact me at laituan245--at--gmail.com
