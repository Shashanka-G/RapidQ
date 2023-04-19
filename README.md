# FlaskApp

Simple application with authentication and CRUD functionality using the Python Flask micro-framework

## Installation

To use this template, your computer needs:

- [Python 2 or 3](https://python.org)
- [Pip Package Manager](https://pypi.python.org/pypi)

### Running the app

```bash
python app.py
```
## INTRODUCTION :
● The question and answer system can address the queries raised by users in their natural
native language on various insurance-related policies, products, and features related to any
corporate efficiently and effectively with an easy to use UI .

● We do have a lot of search engines to do this job, but the problem is they
give the related documents of the query instead of the specific answer the user is looking
for.

● A Questionnaire (QA) is a retrieval system where a direct answer is expected in response
to a submitted question, rather than a set of references that can contain answers.

● The website has been developed using Flask , MySQL ,JavaScript and uses Natural
Language Processing which has been implemented using the RoBERTa(Robustly
Optimized BERT Pre-training Approach) model using haystack .

### The functionalities include :
● Login and signup page :
The user can signup and login in order to use the question and answer system . Token based
authentication has been implemented for this application.

● Query entering and document upload page :
Here the user can upload their insurance document and ask the relevant question in the
query section . The query is processed and the answer is obtained from the document and
the answer will be delivered to the user in a new web page.

● Home page and About us page :
In this page , the user can view information about the creators apart from getting insights
about the various features of the website .

● The Natural Language model that is used to implement the answering of questions
pertaining to the health insurance document is the RoBERTa Model. sThe RoBERTa
model was proposed in RoBERTa: A Robustly Optimized BERT Pretraining Approach.
This is used through haystack and hugging face library.

● It builds on BERT and modifies key hyperparameters, removing the next-sentence
objective and training with much larger mini-batches and learning rates.

● Roberta uses the byte-level Byte-Pair-Encoding method derived from GPT-2. The
vocabulary consists of 50000-word pieces. \U0120 as the unique character is used in the
byte pair encoding, which hasn’t been made visible to us by hugging face. 

## Learnings from the Project

● The project helped us learn about the development of websites using advanced web
technologies like Flask , Javascript and MySQL.

● We also explored various Natural language processing techniques and models such as the
BERT model , Haystack and Hugging face library along with preprocessing of text .

● The use of text retrieval algorithm like the BM25 algorithm ,document reader such as
FarmReader , document storing using Elastic Search and pipelining was explored during
the course of the project.

● The formatting of document text was done using Pymupdf where the documents
uploaded in the pdf format was formatted to text that could be processed by the model.

