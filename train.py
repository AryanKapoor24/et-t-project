import torch
from torch.utils.data import DataLoader, Dataset
from model_config import SimpleLM, VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM
from data_utils import load_data, preprocess, create_vocab

class TextDataset(Dataset):
    def __init__(self, text, vocab):
        self.data = preprocess(text, vocab)
    def __len__(self):
        return len(self.data) - 1
    def __getitem__(self, idx):
        return torch.tensor(self.data[idx]), torch.tensor(self.data[idx+1])

def train():
    text = load_data('data.txt')
    vocab = create_vocab(text)
    dataset = TextDataset(text, vocab)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = SimpleLM(len(vocab), EMBED_DIM, HIDDEN_DIM)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())
    for epoch in range(5):
        for x, y in loader:
            out = model(x)
            loss = criterion(out.view(-1, len(vocab)), y.view(-1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}, Loss: {loss.item()}")

if __name__ == "__main__":
    train()
