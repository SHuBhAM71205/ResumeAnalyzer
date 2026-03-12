# Celery Resume Analyzer

This project is designed to analyze resumes by leveraging Celery for asynchronous task processing. It includes functionalities for storing resume embeddings and comparing them with job embeddings using Qdrant.

## Project Structure

```
celery-resume-analyzer
├── tasks
│   ├── embedding_tasks.py
│   └── comparison_tasks.py
├── config
│   └── celery_config.py
├── requirements.txt
├── celery.py
└── README.md
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd celery-resume-analyzer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

The Celery configuration can be found in `config/celery_config.py`. You may need to adjust the broker URL and other settings based on your environment.

## Tasks

### Embedding Tasks

The `tasks/embedding_tasks.py` file contains tasks related to sending requests to OpenAI or a custom model for storing resume embeddings. The main function exported is:

- `store_resume_embedding(resume_data)`: This function handles the embedding process for the provided resume data.

### Comparison Tasks

The `tasks/comparison_tasks.py` file includes tasks for comparing resume embeddings with job embeddings in Qdrant. The main function exported is:

- `compare_embeddings(resume_embedding, job_embedding)`: This function performs the comparison logic between the resume and job embeddings.

## Usage

To start the Celery worker, run the following command in your terminal:

```
celery -A celery worker --loglevel=info
```

You can then call the tasks from your application as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.