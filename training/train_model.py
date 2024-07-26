import spacy
from spacy.training import Example
import json
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Load the SpaCy model
    nlp = spacy.blank("en")

    # Define the NER component
    ner = nlp.add_pipe("ner")

    # Initialize train_data
    train_data = []

    # Load training data
    with open('training/fixed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    # Check if data is a list
    if isinstance(data, list):
        labels = set()
        for item in data:
            if 'labels' in item:
                for label in item['labels']:
                    labels.add(label)
            if 'training_data' in item:
                for entry in item['training_data']:
                    text = entry['text']
                    annotations = {'entities': [(ent['start'], ent['end'], ent['label']) for ent in entry['points']]}
                    train_data.append((text, annotations))

    # Add labels to the NER component
    for label in labels:
        ner.add_label(label)

    # Begin training
    logger.info("Starting training with %d samples", len(train_data))
    optimizer = nlp.begin_training()
    for epoch in range(10):  # Number of epochs
        logger.info("Epoch %d", epoch + 1)
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.5, losses=losses)
            logger.debug("Losses after example: %s", losses)
        logger.info("Losses: %s", losses)

    # Save the model
    nlp.to_disk("models/custom_ner_model")
    logger.info("Training completed successfully. Model saved to 'models/custom_ner_model'")

except Exception as e:
    logger.error("An error occurred: %s", str(e))
    raise  # Re-raise the exception to be caught by Flask





























