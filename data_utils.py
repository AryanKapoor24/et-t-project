import torch
from collections import Counter

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def preprocess(text, vocab):
    return [vocab.get(token, vocab['<unk>']) for token in text.split()]

def create_vocab(text, max_size=10000):
    tokens = text.split()
    counter = Counter(tokens)
    most_common = counter.most_common(max_size - 2)
    vocab = {'<pad>': 0, '<unk>': 1}
    vocab.update({word: idx+2 for idx, (word, _) in enumerate(most_common)})
    return vocab