import json
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import os

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def format_data(data):
    formatted_data = []
    for item in data:
        text = item['label']
        entities = [(point['start'], point['end'], point['label']) for point in item['points']]
        formatted_data.append((text, {"entities": entities}))
    return formatted_data

# Load and format the data
data = format_data(load_data('training/fixed_data.json'))  # Use your single JSON file

# Split the data into training and test sets (80% training, 20% test)
random.shuffle(data)
split = int(len(data) * 0.8)
train_data = data[:split]
test_data = data[split:]

# Load blank English model
nlp = spacy.blank('en')

# Create a new entity recognizer
if 'ner' not in nlp.pipe_names:
    ner = nlp.add_pipe('ner', last=True)
else:
    ner = nlp.get_pipe('ner')

# Add labels
for _, annotations in train_data:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for i in range(20):  # Number of training iterations
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            examples = []
            for text, annot in zip(texts, annotations):
                if not isinstance(text, str):
                    print(f"Text is not a string: {text}")
                    continue
                if not isinstance(annot, dict):
                    print(f"Annotation is not a dictionary: {annot}")
                    continue
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annot)
                examples.append(example)
            nlp.update(examples, drop=0.5, losses=losses)
        print(f"Losses at iteration {i}: {losses}")

# Save the trained model
output_dir = "models/custom_ner_model"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nlp.to_disk(output_dir)
print(f"Model saved to {output_dir}")
























