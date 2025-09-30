# Movie Search Demo with Weaviate

A semantic movie search application powered by Weaviate and Gradio.

## Project Structure

```
├── main.py                 # Main application entry point
├── weaviate_service.py     # Weaviate database operations
├── gradio_interface.py     # Gradio UI components
├── pyproject.toml          # Project dependencies
└── README.md              # This file
```

## Features

- **Semantic Search**: Search movies using natural language queries
- **Vector Database**: Powered by Weaviate for efficient similarity search
- **Web Interface**: Clean Gradio-based UI
- **Auto-initialization**: Automatically sets up database and imports data on first run

## Installation

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Set up environment variables in `.env`:
   ```
   OPENAI_APIKEY=your_openai_api_key
   WEAVIATE_HOST=localhost
   WEAVIATE_PORT=8080
   ```

## Usage

Run the application:

```bash
uv run main.py
```

Then open your browser to `http://localhost:8008` and start searching for movies!

## Architecture

- **`main.py`**: Orchestrates the application, initializes services, and launches the web interface
- **`weaviate_service.py`**: Handles all Weaviate operations (collection creation, data import, search)
- **`gradio_interface.py`**: Manages the Gradio UI components and user interactions



