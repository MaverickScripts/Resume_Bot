# -*- coding: utf-8 -*-
"""RESUME_BOT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18DqjJgwuQgO5qEKLBDJm_-hPr2MB4zji
"""

!pip install scikit-learn

!pip install PyPDF2

!pip install transformers

import os
import time
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import shutil
import PyPDF2

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# Initialize BERT pipeline for feature extraction
nlp = pipeline("feature-extraction", model=model, tokenizer=tokenizer)

# Define the function to extract features from a text
def extract_features(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to score resumes based on job description and keywords
def score_resume(resume_text, job_text, keywords):
    resume_features = extract_features(resume_text)
    job_features = extract_features(job_text)

    # Compute cosine similarity between resume and job description
    similarity = cosine_similarity(resume_features, job_features)[0][0]

    # Compute keyword match score
    keyword_score = sum([resume_text.lower().count(keyword.lower()) for keyword in keywords]) / len(keywords)

    # Combine similarity and keyword scores
    combined_score = similarity * 0.7 + keyword_score * 0.3

    return combined_score

# Function to read PDF and extract text
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

# Function to process resumes and save top ones
def process_resumes(input_path, job_description, keywords, output_folder, top_n):
    start_time = time.time()

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    resumes = []
    scores = []
    explanations = []
    excluded = []

    # Check if input path is a file or folder
    if os.path.isfile(input_path):
        # Process single PDF file
        resume_text = read_pdf(input_path)
        if not resume_text:
            excluded.append((os.path.basename(input_path), "Unreadable PDF or empty text"))
        elif len(resume_text.split()) < 50:
            excluded.append((os.path.basename(input_path), "Insufficient length"))
        else:
            score = score_resume(resume_text, job_description, keywords)
            filename = os.path.basename(input_path)
            resumes.append((filename, resume_text, score))
    else:
        # Process all PDF files in the folder
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                resume_text = read_pdf(file_path)
                if not resume_text:
                    excluded.append((filename, "Unreadable PDF or empty text"))
                elif len(resume_text.split()) < 50:
                    excluded.append((filename, "Insufficient length"))
                else:
                    score = score_resume(resume_text, job_description, keywords)
                    resumes.append((filename, resume_text, score))

    # Create a DataFrame to display scores
    df = pd.DataFrame(resumes, columns=["Filename", "Resume", "Score"])

    # Sort resumes by score
    df = df.sort_values(by="Score", ascending=False)

    # Save top resumes
    for i in range(min(top_n, len(df))):
        filename = df.iloc[i]["Filename"]
        score = df.iloc[i]["Score"]
        resume_text = df.iloc[i]["Resume"]

        # Save the resume file
        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(output_folder, filename))
        else:
            shutil.copy(os.path.join(input_path, filename), output_folder)

        # Create an explanation
        explanation = f"Chosen because it has a similarity score of {score:.4f} with the job description and keywords."
        explanations.append((filename, explanation))

    # Save explanations to a file
    with open(os.path.join(output_folder, "explanations.txt"), 'w') as file:
        for filename, explanation in explanations:
            file.write(f"{filename}: {explanation}\n")

    # Save exclusions to a file (including non-top resumes)
    with open(os.path.join(output_folder, "exclusions.txt"), 'w') as file:
        for filename, reason in excluded:
            file.write(f"{filename}: {reason}\n")
        for i in range(top_n, len(df)):
            filename = df.iloc[i]["Filename"]
            score = df.iloc[i]["Score"]
            file.write(f"{filename}: Not in the top {top_n} scores (score: {score:.4f})\n")

    end_time = time.time()

    # Performance Metrics
    processing_time = end_time - start_time
    num_resumes_processed = len(resumes) + len(excluded)
    num_resumes_selected = len(df.head(top_n))
    average_similarity_score = np.mean([score for _, _, score in resumes]) if resumes else 0
    average_selected_similarity_score = np.mean(df.head(top_n)["Score"]) if not df.head(top_n).empty else 0

    metrics = {
        "Processing Time (seconds)": processing_time,
        "Number of Resumes Processed": num_resumes_processed,
        "Number of Resumes Selected": num_resumes_selected,
        "Average Similarity Score": average_similarity_score,
        "Average Selected Similarity Score": average_selected_similarity_score
    }

    # Print performance metrics
    print("Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    return df

# User input for resume folder or file, job description, keywords, and number of resumes to select
input_path = input("Enter the path to the resume folder or PDF file: ")
job_description = input("Enter the job description: ")
keywords = input("Enter keywords (comma-separated): ").split(",")
top_n = int(input("Enter the number of resumes to select: "))

output_folder = "selected_resumes"

# Process resumes and save top ones
top_resumes_df = process_resumes(input_path, job_description, keywords, output_folder, top_n)
print(top_resumes_df)

import os
import time
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import shutil
import PyPDF2

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# Initialize BERT pipeline for feature extraction
nlp = pipeline("feature-extraction", model=model, tokenizer=tokenizer)

# Define the function to extract features from a text
def extract_features(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to score resumes based on job description and keywords
def score_resume(resume_text, job_text, keywords):
    resume_features = extract_features(resume_text)
    job_features = extract_features(job_text)

    # Compute cosine similarity between resume and job description
    similarity = cosine_similarity(resume_features, job_features)[0][0]

    # Compute keyword match score
    keyword_score = sum([resume_text.lower().count(keyword.lower()) for keyword in keywords]) / len(keywords)

    # Combine similarity and keyword scores
    combined_score = similarity * 0.7 + keyword_score * 0.3

    return combined_score

# Function to read PDF and extract text
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

# Function to process resumes and save top ones
def process_resumes(input_path, job_description, keywords, output_folder, top_n):
    start_time = time.time()

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    resumes = []
    scores = []
    explanations = []
    excluded = []

    # Check if input path is a file or folder
    if os.path.isfile(input_path):
        # Process single PDF file
        resume_text = read_pdf(input_path)
        if not resume_text:
            excluded.append((os.path.basename(input_path), "Unreadable PDF or empty text"))
        elif len(resume_text.split()) < 50:
            excluded.append((os.path.basename(input_path), "Insufficient length"))
        else:
            score = score_resume(resume_text, job_description, keywords)
            filename = os.path.basename(input_path)
            resumes.append((filename, resume_text, score))
    else:
        # Process all PDF files in the folder
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                resume_text = read_pdf(file_path)
                if not resume_text:
                    excluded.append((filename, "Unreadable PDF or empty text"))
                elif len(resume_text.split()) < 50:
                    excluded.append((filename, "Insufficient length"))
                else:
                    score = score_resume(resume_text, job_description, keywords)
                    resumes.append((filename, resume_text, score))

    # Create a DataFrame to display scores
    df = pd.DataFrame(resumes, columns=["Filename", "Resume", "Score"])

    # Sort resumes by score
    df = df.sort_values(by="Score", ascending=False)

    # Save top resumes
    for i in range(min(top_n, len(df))):
        filename = df.iloc[i]["Filename"]
        score = df.iloc[i]["Score"]
        resume_text = df.iloc[i]["Resume"]

        # Save the resume file
        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(output_folder, filename))
        else:
            shutil.copy(os.path.join(input_path, filename), output_folder)

        # Create an explanation
        explanation = f"Chosen because it has a similarity score of {score:.4f} with the job description and keywords."
        explanations.append((filename, explanation))

    # Save explanations to a file
    with open(os.path.join(output_folder, "explanations.txt"), 'w') as file:
        for filename, explanation in explanations:
            file.write(f"{filename}: {explanation}\n")

    # Save exclusions to a file (including non-top resumes)
    with open(os.path.join(output_folder, "exclusions.txt"), 'w') as file:
        for filename, reason in excluded:
            file.write(f"{filename}: {reason}\n")
        for i in range(top_n, len(df)):
            filename = df.iloc[i]["Filename"]
            score = df.iloc[i]["Score"]
            file.write(f"{filename}: Not in the top {top_n} scores (score: {score:.4f})\n")

    end_time = time.time()

    # Performance Metrics
    processing_time = end_time - start_time
    num_resumes_processed = len(resumes) + len(excluded)
    num_resumes_selected = len(df.head(top_n))
    average_similarity_score = np.mean([score for _, _, score in resumes]) if resumes else 0
    average_selected_similarity_score = np.mean(df.head(top_n)["Score"]) if not df.head(top_n).empty else 0

    metrics = {
        "Processing Time (seconds)": processing_time,
        "Number of Resumes Processed": num_resumes_processed,
        "Number of Resumes Selected": num_resumes_selected,
        "Average Similarity Score": average_similarity_score,
        "Average Selected Similarity Score": average_selected_similarity_score
    }

    # Print performance metrics
    print("Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    return df

# Main function to capture input and run the process
def main():
    # User input for resume folder or file, job description, keywords, and number of resumes to select
    input_path = input("Enter the path to the resume folder or PDF file: ")
    job_description = input("Enter the job description: ")
    keywords = input("Enter keywords (comma-separated): ").split(",")
    top_n = int(input("Enter the number of resumes to select: "))

    output_folder = "selected_resumes"

    # Process resumes and save top ones
    top_resumes_df = process_resumes(input_path, job_description, keywords, output_folder, top_n)
    print(top_resumes_df)

# Record the actual start time
overall_start_time = time.time()

# Run the main function
main()

# Record the actual end time
overall_end_time = time.time()

# Calculate the overall processing time
overall_processing_time = overall_end_time - overall_start_time
print(f"Overall Processing Time (seconds): {overall_processing_time}")

import os
import time
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
import shutil
import PyPDF2

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# Initialize BERT pipeline for feature extraction
nlp = pipeline("feature-extraction", model=model, tokenizer=tokenizer)

# Define the function to extract features from a text
def extract_features(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to score resumes based on job description and keywords
def score_resume(resume_text, job_text, keywords):
    resume_features = extract_features(resume_text)
    job_features = extract_features(job_text)

    # Compute cosine similarity between resume and job description
    similarity = cosine_similarity(resume_features, job_features)[0][0]

    # Compute keyword match score
    keyword_score = sum([resume_text.lower().count(keyword.lower()) for keyword in keywords]) / len(keywords)

    # Combine similarity and keyword scores
    combined_score = similarity * 0.7 + keyword_score * 0.3

    return combined_score

# Function to read PDF and extract text
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

# Function to process resumes and save top ones
def process_resumes(input_path, job_description, keywords, output_folder, top_n):
    start_time = time.time()

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    resumes = []
    scores = []
    explanations = []
    excluded = []

    # Check if input path is a file or folder
    if os.path.isfile(input_path):
        # Process single PDF file
        resume_text = read_pdf(input_path)
        if not resume_text:
            excluded.append((os.path.basename(input_path), "Unreadable PDF or empty text"))
        elif len(resume_text.split()) < 50:
            excluded.append((os.path.basename(input_path), "Insufficient length"))
        else:
            score = score_resume(resume_text, job_description, keywords)
            filename = os.path.basename(input_path)
            resumes.append((filename, resume_text, score))
    else:
        # Process all PDF files in the folder
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                resume_text = read_pdf(file_path)
                if not resume_text:
                    excluded.append((filename, "Unreadable PDF or empty text"))
                elif len(resume_text.split()) < 50:
                    excluded.append((filename, "Insufficient length"))
                else:
                    score = score_resume(resume_text, job_description, keywords)
                    resumes.append((filename, resume_text, score))

    # Create a DataFrame to display scores
    df = pd.DataFrame(resumes, columns=["Filename", "Resume", "Score"])

    # Sort resumes by score
    df = df.sort_values(by="Score", ascending=False)

    # Save top resumes
    for i in range(min(top_n, len(df))):
        filename = df.iloc[i]["Filename"]
        score = df.iloc[i]["Score"]
        resume_text = df.iloc[i]["Resume"]

        # Save the resume file
        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(output_folder, filename))
        else:
            shutil.copy(os.path.join(input_path, filename), output_folder)

        # Create an explanation
        explanation = f"Chosen because it has a similarity score of {score:.4f} with the job description and keywords."
        explanations.append((filename, explanation))

    # Save explanations to a file
    with open(os.path.join(output_folder, "explanations.txt"), 'w') as file:
        for filename, explanation in explanations:
            file.write(f"{filename}: {explanation}\n")

    # Save exclusions to a file (including non-top resumes)
    with open(os.path.join(output_folder, "exclusions.txt"), 'w') as file:
        for filename, reason in excluded:
            file.write(f"{filename}: {reason}\n")
        for i in range(top_n, len(df)):
            filename = df.iloc[i]["Filename"]
            score = df.iloc[i]["Score"]
            file.write(f"{filename}: Not in the top {top_n} scores (score: {score:.4f})\n")

    end_time = time.time()

    # Performance Metrics
    processing_time = end_time - start_time
    num_resumes_processed = len(resumes) + len(excluded)
    num_resumes_selected = len(df.head(top_n))
    average_similarity_score = np.mean([score for _, _, score in resumes]) if resumes else 0
    average_selected_similarity_score = np.mean(df.head(top_n)["Score"]) if not df.head(top_n).empty else 0

    # Precision, Recall, and F1 Score Calculation
    true_positive = len(df.head(top_n))
    false_positive = num_resumes_processed - true_positive
    false_negative = len(resumes) - true_positive

    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    metrics = {
        "Processing Time (seconds)": processing_time,
        "Number of Resumes Processed": num_resumes_processed,
        "Number of Resumes Selected": num_resumes_selected,
        "Average Similarity Score": average_similarity_score,
        "Average Selected Similarity Score": average_selected_similarity_score,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }

    # Print performance metrics
    print("Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    return df

# User input for resume folder or file, job description, keywords, and number of resumes to select
input_path = input("Enter the path to the resume folder or PDF file: ")
job_description = input("Enter the job description: ")
keywords = input("Enter keywords (comma-separated): ").split(",")
top_n = int(input("Enter the number of resumes to select: "))

output_folder = "selected_resumes"

# Process resumes and save top ones
top_resumes_df = process_resumes(input_path, job_description, keywords, output_folder, top_n)
print(top_resumes_df)



!pip install datasets

from google.colab import drive
drive.mount('/content/drive')

import os
import PyPDF2

# Function to read PDF and extract text
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

# Extract text from all PDF files in a folder
def extract_text_from_folder(folder_path):
    resumes = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            resume_text = read_pdf(file_path)
            if resume_text and len(resume_text.split()) >= 50:  # Ensure the resume is not empty and has sufficient length
                resumes.append((filename, resume_text))
    return resumes

# Path to the folder containing PDF files
folder_path = "/content/drive/MyDrive/resume"

resumes = extract_text_from_folder(folder_path)
print(f"Extracted text from {len(resumes)} resumes.")

import os
import PyPDF2

# Function to read PDF and extract text
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

# Extract text from all PDF files in a folder
def extract_text_from_folder(folder_path):
    resumes = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            resume_text = read_pdf(file_path)
            if resume_text and len(resume_text.split()) >= 50:  # Ensure the resume is not empty and has sufficient length
                resumes.append((filename, resume_text))
    return resumes

# Path to the folder containing PDF files
folder_path = "/content/drive/MyDrive/resume"

resumes = extract_text_from_folder(folder_path)
print(f"Extracted text from {len(resumes)} resumes.")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

# Convert resume texts to TF-IDF features
def vectorize_texts(resume_texts):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    vectors = vectorizer.fit_transform(resume_texts)
    return vectors

# Apply K-Means clustering
def cluster_resumes(resumes, n_clusters=2):
    resume_texts = [text for _, text in resumes]
    vectors = vectorize_texts(resume_texts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(vectors)
    labels = kmeans.labels_
    return labels

# Cluster resumes
labels = cluster_resumes(resumes, n_clusters=2)

# Combine resumes with their labels
labeled_resumes = [(filename, text, label) for (filename, text), label in zip(resumes, labels)]
df = pd.DataFrame(labeled_resumes, columns=["Filename", "Resume", "Label"])
print(df.head())

from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import numpy as np
import torch
from sklearn.model_selection import train_test_split

# Function to prepare dataset for fine-tuning
def prepare_dataset(resumes, labels):
    df = pd.DataFrame({'text': resumes, 'label': labels})
    train_df, eval_df = train_test_split(df, test_size=0.2, random_state=42)
    train_dataset = Dataset.from_pandas(train_df)
    eval_dataset = Dataset.from_pandas(eval_df)
    return train_dataset, eval_dataset

# Prepare data
resumes = df["Resume"].tolist()
labels = df["Label"].tolist()
train_dataset, eval_dataset = prepare_dataset(resumes, labels)

# Load and fine-tune BERT
def fine_tune_bert(train_dataset, eval_dataset):
    model_name = "bert-base-uncased"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True)

    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
    )

    trainer.train()
    model.save_pretrained('./resume_classifier_model')
    tokenizer.save_pretrained('./resume_classifier_model')

# Fine-tune BERT model
fine_tune_bert(train_dataset, eval_dataset)

import shutil
import time

# Function to score resumes based on fine-tuned BERT model
def score_resume(resume_text, model, tokenizer):
    inputs = tokenizer(resume_text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    return probabilities[0][1].item()  # Probability of the positive class

# Function to process resumes and save top ones
def process_resumes(input_path, job_description, keywords, output_folder, top_n):
    start_time = time.time()

    # Load fine-tuned BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained('./resume_classifier_model')
    model = BertForSequenceClassification.from_pretrained('./resume_classifier_model')

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    resumes = []
    scores = []
    explanations = []
    excluded = []

    # Check if input path is a file or folder
    if os.path.isfile(input_path):
        # Process single PDF file
        resume_text = read_pdf(input_path)
        if not resume_text:
            excluded.append((os.path.basename(input_path), "Unreadable PDF or empty text"))
        elif len(resume_text.split()) < 50:
            excluded.append((os.path.basename(input_path), "Insufficient length"))
        else:
            score = score_resume(resume_text, model, tokenizer)
            filename = os.path.basename(input_path)
            resumes.append((filename, resume_text, score))
    else:
        # Process all PDF files in the folder
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                resume_text = read_pdf(file_path)
                if not resume_text:
                    excluded.append((filename, "Unreadable PDF or empty text"))
                elif len(resume_text.split()) < 50:
                    excluded.append((filename, "Insufficient length"))
                else:
                    score = score_resume(resume_text, model, tokenizer)
                    resumes.append((filename, resume_text, score))

    # Create a DataFrame to display scores
    df = pd.DataFrame(resumes, columns=["Filename", "Resume", "Score"])

    # Sort resumes by score
    df = df.sort_values(by="Score", ascending=False)

    # Save top resumes
    for i in range(min(top_n, len(df))):
        filename = df.iloc[i]["Filename"]
        score = df.iloc[i]["Score"]
        resume_text = df.iloc[i]["Resume"]

        # Save the resume file
        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(output_folder, filename))
        else:
            shutil.copy(os.path.join(input_path, filename), output_folder)

        # Create an explanation
        explanation = f"Chosen because it has a classification score of {score:.4f} with the job description and keywords."
        explanations.append((filename, explanation))

    # Save explanations to a file
    with open(os.path.join(output_folder, "explanations.txt"), 'w') as file:
        for filename, explanation in explanations:
            file.write(f"{filename}: {explanation}\n")

    # Save exclusions to a file (including non-top resumes)
    with open(os.path.join(output_folder, "exclusions.txt"), 'w') as file:
        for filename, reason in excluded:
            file.write(f"{filename}: {reason}\n")
        for i in range(top_n, len(df)):
            filename = df.iloc[i]["Filename"]
            score = df.iloc[i]["Score"]
            file.write(f"{filename}: Not in the top {top_n} scores (score: {score:.4f})\n")

    end_time = time.time()

    # Performance Metrics
    processing_time = end_time - start_time
    num_resumes_processed = len(resumes) + len(excluded)
    num_resumes_selected = len(df.head(top_n))
    average_score = np.mean([score for _, _, score in resumes]) if resumes else 0
    average_selected_score = np.mean(df.head(top_n)["Score"]) if not df.head(top_n).empty else 0

    metrics = {
        "Processing Time (seconds)": processing_time,
        "Number of Resumes Processed": num_resumes_processed,
        "Number of Resumes Selected": num_resumes_selected,
        "Average Score": average_score,
        "Average Selected Score": average_selected_score
    }

    # Print performance metrics
    print("Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    return df

# User input for resume folder or file, job description, keywords, output folder, and top N resumes
input_path = "/content/drive/MyDrive/resume"
job_description = "web developer, data scientist"
keywords = ["python", "numpy", "node js"]
output_folder = "path_to_output_folder"
top_n = 4

# Process resumes
df = process_resumes(input_path, job_description, keywords, output_folder, top_n)

def extract_features(text):                            #function to extract text from pdf
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def score_resume(resume_text, job_text, keywords):                   #storing resume text,job text,keywords
    resume_features = extract_features(resume_text)
    job_features = extract_features(job_text)

    similarity = cosine_similarity(resume_features, job_features)[0][0]           #compute cosine_similarity between resume and job feature

    keyword_score = sum([resume_text.lower().count(keyword.lower()) for keyword in keywords]) / len(keywords)                               #keyword match score
    combined_score = similarity * 0.7 + keyword_score * 0.3             #combine keyword_score and similarity score

    return combined_score

def read_pdf(file_path):                         #reading the pdf file and extract the text
    pdf_text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            pdf_text += page.extract_text() or ""
    return pdf_text

def process_resumes(input_path, job_description, keywords, output_folder, top_n):
    start_time = time.time()       #time

    if not os.path.exists(output_folder):                #output folder
        os.makedirs(output_folder)

    resumes = []
    scores = []
    explanations = []
    excluded = []

    if os.path.isfile(input_path):
        resume_text = read_pdf(input_path)            #it will basically check if single file/a folder is the input
        if not resume_text:
            excluded.append((os.path.basename(input_path), "Unreadable PDF or empty text"))            #check for exclusions
        elif len(resume_text.split()) < 50:
            excluded.append((os.path.basename(input_path), "Insufficient length"))
        else:
            score = score_resume(resume_text, job_description, keywords)
            filename = os.path.basename(input_path)
            resumes.append((filename, resume_text, score))
    else:
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                resume_text = read_pdf(file_path)
                if not resume_text:
                    excluded.append((filename, "Unreadable PDF or empty text"))
                elif len(resume_text.split()) < 50:
                    excluded.append((filename, "Insufficient length"))
                else:
                    score = score_resume(resume_text, job_description, keywords)
                    resumes.append((filename, resume_text, score))

    df = pd.DataFrame(resumes, columns=["Filename", "Resume", "Score"])     #df containing scores

    df = df.sort_values(by="Score", ascending=False)          #sorting the dataset with score

    for i in range(min(top_n, len(df))):           #save the top resumes
        filename = df.iloc[i]["Filename"]
        score = df.iloc[i]["Score"]
        resume_text = df.iloc[i]["Resume"]

        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(output_folder, filename))
        else:
            shutil.copy(os.path.join(input_path, filename), output_folder)

        explanation = f"Chosen because it has a similarity score of {score:.4f} with the job description and keywords."             #basically the statements in the explanations.txt file
        explanations.append((filename, explanation))

    with open(os.path.join(output_folder, "explanations.txt"), 'w') as file:            #save explanations of the files selected
        for filename, explanation in explanations:
            file.write(f"{filename}: {explanation}\n")

    with open(os.path.join(output_folder, "exclusions.txt"), 'w') as file:            #save exclusions of file non selected
        for filename, reason in excluded:
            file.write(f"{filename}: {reason}\n")
        for i in range(top_n, len(df)):
            filename = df.iloc[i]["Filename"]
            score = df.iloc[i]["Score"]
            file.write(f"{filename}: Not in the top {top_n} scores (score: {score:.4f})\n")

    end_time = time.time()

    processing_time = end_time - start_time                                    #performance metrics
    num_resumes_processed = len(resumes) + len(excluded)
    num_resumes_selected = len(df.head(top_n))
    average_similarity_score = np.mean([score for _, _, score in resumes]) if resumes else 0
    average_selected_similarity_score = np.mean(df.head(top_n)["Score"]) if not df.head(top_n).empty else 0

    metrics = {
        "Processing Time (seconds)": processing_time,
        "Number of Resumes Processed": num_resumes_processed,
        "Number of Resumes Selected": num_resumes_selected,
        "Average Similarity Score": average_similarity_score,
        "Average Selected Similarity Score": average_selected_similarity_score
    }
    print("Performance Metrics:")                             #printing of performance metrics
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    return df
input_path = input("Enter the path to the resume folder or PDF file: ")
job_description = input("Enter the job description: ")                              #user input for resume path,keywords,job description,number of top resumes to select
keywords = input("Enter keywords (comma-separated): ").split(",")
top_n = int(input("Enter the number of resumes to select: "))

output_folder = "selected_resumes"

top_resumes_df = process_resumes(input_path, job_description, keywords, output_folder, top_n)     #process the resume and save the no. of resumes wanted
print(top_resumes_df)