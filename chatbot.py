#link tham khảo: https://viblo.asia/p/ap-dung-machine-learning-xay-dung-ung-dung-chatbot-cua-rieng-ban-3P0lPk38Zox
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import pickle
import datetime
import sqlite3
from tkinter import*

with open('json.json') as json_data:
    intents = json.load(json_data)
words = []
classes = []
documents = []
stop_words = ['?', 'a', 'an', 'the']

for intent in intents['intents']:
    for pattern in intent['patterns']:

        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [stemmer.stem(w.lower()) for w in words if w not in stop_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

training = []
output = []
output_empty = [0] * len(classes)
# training set, bag of words for each sentence
for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])
random.shuffle(training)
training = np.array(training)
# create train and test lists
train_x = list(training[:,0])
train_y = list(training[:,1])
tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')
# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# Start training
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')
pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']
# import intents file
with open('json.json') as json_data:
    intents = json.load(json_data)
model.load('./model.tflearn')
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words
# bag of words
def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: {s}".format(w))

    return np.array(bag)

bow("Ten ban la gi?", words)
context = {}
ERROR_THRESHOLD = 0.25
def classify(sentence):
    results = model.predict([bow(sentence, words)])[0]
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list

def response(sentence, userID='1', show_details=False):
    results = classify(sentence)
    if results:
        while results:
            for i in intents['intents']:
                if i['tag'] == results[0][0]:
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: 
                            print ('tag:', i['tag'])
                        return random.choice(i['responses'])

            results.pop(0)
root = Tk()
root.geometry("600x260")
def btn_ghi():
    cauhoi = lbl.get()
    lbl3.configure(text=cauhoi)
    a = response(cauhoi)
    lbl4.configure(text=a)  

lbl1 = Label(root, text='Câu hỏi', font=("Times New Roman",14), fg='green')
lbl1.place(x=5, y=220)       
lbl = Entry(root, width=45, font=("Times New Roman",14))
lbl.place(x=85, y=220)
btn = Button(root, text="gửi", font=("Times New Roman", 14), fg="white", bg="green",width=10, height=1, command=btn_ghi)
btn.place(x=480, y=217)
lbl2 = Label(root, text= "Câu hỏi: ", font=("Times New Roman", 14), fg="red")
lbl2.place(x=10, y =10)
lbl3 = Label(root, text= " ", font=("Times New Roman", 14), fg="green")
lbl3.place(x=80, y =10)
lbl5 = Label(root, text= "Câu trả lời: ", font=("Times New Roman", 14), fg="red")
lbl5.place(x=10, y = 40)
lbl4 = Label(root, text= " ", font=("Times New Roman", 14), fg="green")
lbl4.place(x=30, y =70)
root.mainloop()