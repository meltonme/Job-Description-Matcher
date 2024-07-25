import json
import spacy
from spacy.training import Example
import random

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8', errors='replace') as f:
        data = json.load(f)
        print("Loaded data:", data)  # Debugging output
        return data

def format_data(data):
    formatted_data = []
    for item in data:
        print("Item:", item)  # Debugging output
        if isinstance(item, dict):  # Ensure item is a dictionary
            text = item.get('label')
            points = item.get('points')
            if text is None or points is None:
                print(f"Warning: Missing 'label' or 'points' in item - {item}")
                continue  # Skip this item
            entities = [(point['start'], point['end'], point['label']) for point in points]
            formatted_data.append((text, {"entities": entities}))
        else:
            print(f"Warning: Expected dictionary but got {type(item)} - {item}")
    return formatted_data

train_data = format_data(load_data('traindata.json'))
test_data = format_data(load_data('testdata.json'))

# Create a blank SpaCy model and add NER component
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add labels to the NER component
for _, annotations in train_data:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other components in the pipeline to train only NER
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for i in range(20):
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            example = Example.from_dict(nlp.make_doc(text), annotations)
            nlp.update([example], drop=0.5, losses=losses)
        print(losses)

# Save the trained model
model_path = "models/custom_ner_model"
nlp.to_disk(model_path)




