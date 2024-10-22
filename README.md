# Resume_Bot
This project is a Resume Matching Bot designed to analyze resumes and compare them with job descriptions. It uses NLP models from the transformers library and techniques such as cosine similarity to match resumes with job requirements efficiently. The bot can read PDFs, extract text from resumes, and measure similarity between candidate profiles and job descriptions.

Features
Resume Parsing: Extracts text from resumes in PDF format using PyPDF2.
Job Matching: Uses BERT (Bidirectional Encoder Representations from Transformers) to generate embeddings for the resumes and job descriptions.
Cosine Similarity: Measures how well a resume matches a given job description.
Batch Processing: Supports multiple resume files for comparison.
Dependencies
Make sure to install the required Python libraries. You can install them using the following commands:

bash
Copy code
pip install scikit-learn
pip install PyPDF2
pip install transformers
How it Works
PDF Extraction: The resumes are provided in PDF format. The bot extracts text from these files using the PyPDF2 library.
BERT Embeddings: Both job descriptions and resumes are converted into vector embeddings using the pre-trained BERT model.
Cosine Similarity: The similarity between the job description and the resume is calculated using cosine similarity.
Result Output: The script displays similarity scores, helping recruiters identify the most relevant resumes for a job posting.
Usage Instructions
Organize Files:

Place your job descriptions and resumes in appropriate directories.
Run the Script:

Open a terminal or Jupyter notebook.

Run the following command to start the script:

bash
Copy code
python resume_bot.py
Example Workflow:

The script will prompt for input directories containing resumes and job descriptions.
It will calculate similarity scores and display them in the console or save them to a file.
Code Structure
PDF Reading: Extracts text from PDF resumes using PyPDF2.
BERT Embedding: Uses the transformers library to generate vector representations.
Similarity Calculation: Compares the embeddings using cosine_similarity from scikit-learn.
Output Handling: Displays results or saves them for future analysis.
Potential Improvements
Integrate more advanced NLP models such as Sentence-BERT for better similarity scores.
Build a Graphical User Interface (GUI) for ease of use.
Add support for other document formats (e.g., DOCX).
Implement cloud support to handle larger datasets.
Contributing
Feel free to open issues or contribute by submitting pull requests. Ensure that any changes are properly documented.

License
This project is licensed under the MIT License - see the LICENSE file for details.

This README.md provides a structured overview, making it easier for others to understand the purpose and functionality of your resume bot project. If you need further adjustments or detailed explanations on specific parts of the code, let me know! ​
