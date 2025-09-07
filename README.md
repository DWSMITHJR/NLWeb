# NLWeb AutoRAG

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-brightgreen)](https://github.com/DWSMITHJR/NLWeb)


A Windows-based Natural Language Web Application with AutoML-powered Retrieval-Augmented Generation (RAG) capabilities, featuring hybrid retrieval and prompt template optimization.

## Features

- **Hybrid Retrieval System**: Combines BM25 and FAISS retrievers for improved search accuracy
- **AutoML Optimization**: Automatically finds the best configuration for your documents
- **Multiple Prompt Templates**: Choose from various prompt engineering strategies
- **Document Processing**: Advanced chunking with multiple strategies (fixed, sentence, paragraph)
- **Evaluation Metrics**: Comprehensive metrics for retrieval and answer quality
- **Natural Language Interface**: Intuitive query interface with context-aware responses
- **Document Management**: Easy document upload and management
- **Modern UI**: Responsive design with dark mode support

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Windows 10/11
- Git (recommended for development)

## Setup

### Backend Setup

1. Clone the repository (if you haven't already):
   ```powershell
   git clone <repository-url>
   cd NLWeb-AutoRAG
   ```

2. Navigate to the backend directory:
   ```bash
   cd backend
   ```

3. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For development and testing
   ```

5. Start the backend server:
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### AutoML Configuration

The AutoML system can be configured using the following environment variables:

```powershell
# AutoML configuration (Windows PowerShell)
$env:AUTOML_MAX_WORKERS = 4  # Number of parallel workers
$env:AUTOML_OUTPUT_DIR = "./automl_results"  # Directory to store results
$env:AUTOML_MAX_CONFIGS = 20  # Maximum number of configurations to test
$env:AUTOML_MAX_ITERATIONS = 10  # Maximum optimization iterations
```

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

## Usage

### Basic Usage

1. **Add Documents**: Upload documents to build your knowledge base
2. **Query Interface**: Ask questions in natural language
3. **View Results**: Get answers with source references and confidence scores

### Advanced Features

#### AutoML Optimization

```python
from automl.orchestrator import AutoMLOrchestrator
from models import Document

# Initialize AutoML
automl = AutoMLOrchestrator(
    output_dir="./automl_results",
    max_workers=4
)

# Run optimization
results = automl.run(
    train_documents=documents,
    test_queries=test_queries,
    num_configs=10,
    max_iterations=5
)
```

#### Prompt Template Management

```python
from prompt_templates import PromptTemplateManager, TemplateType

# Get template manager
manager = PromptTemplateManager()

# List available templates
print(manager.list_templates())

# Get a specific template
template = manager.get_template(TemplateType.STEP_BY_STEP)
formatted = template.format(
    context="Your context here",
    question="Your question here"
)
```

## API Endpoints

### Document Management
- `POST /documents/` - Add a new document
- `GET /documents/` - List all documents
- `GET /documents/{doc_id}` - Get a specific document
- `DELETE /documents/{doc_id}` - Delete a document

### Query Endpoints
- `POST /query/` - Query the knowledge base
- `GET /query/history` - Get query history

### AutoML Endpoints
- `POST /automl/start` - Start AutoML optimization
- `GET /automl/status/{job_id}` - Check job status
- `GET /automl/results/{job_id}` - Get optimization results

## Project Structure

```
.
├── backend/                      # FastAPI backend
│   ├── api/                     # API routes
│   │   └── routers/             # API routers
│   ├── automl/                  # AutoML components
│   │   ├── retrievers/          # Retriever implementations
│   │   ├── config.py            # Configuration management
│   │   └── orchestrator.py      # AutoML orchestration
│   ├── document_processor.py    # Document processing logic
│   ├── evaluation.py            # Evaluation metrics
│   ├── main.py                 # Main application file
│   ├── models.py               # Data models
│   ├── prompt_templates.py     # Prompt template management
│   └── requirements.txt        # Python dependencies
│
└── frontend/                   # React frontend
    ├── public/                 # Static files
    └── src/                    # Source files
        ├── components/         # React components
        ├── App.js              # Main React component
        └── index.js            # Entry point
```

## Testing

Run the test suite:

```powershell
# Activate virtual environment first
.\venv\Scripts\activate

# Run all tests
python -m pytest

# Run specific test
python test_automl_integration.py
```

## Development

### Adding New Retrievers
1. Create a new file in `backend/automl/retrievers/`
2. Implement the `BaseRetriever` interface
3. Update the `AutoMLOrchestrator._create_retriever()` method

### Adding New Prompt Templates
1. Add a new `TemplateType` enum value
2. Add the template to `PromptTemplateManager._load_default_templates()`
3. The template will be automatically included in the AutoML search space

## Troubleshooting

### Common Issues

1. **Dependency Installation**
   - Ensure you're using Python 3.8+
   - Try upgrading pip: `python -m pip install --upgrade pip`
   - On Windows, you might need C++ build tools for some packages

2. **Performance Issues**
   - Reduce `max_workers` if you encounter memory issues
   - Decrease `num_configs` or `max_iterations` for faster testing

3. **Model Loading**
   - Some embedding models require internet access for first-time download
   - Check your internet connection and proxy settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT

## Acknowledgements

- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
