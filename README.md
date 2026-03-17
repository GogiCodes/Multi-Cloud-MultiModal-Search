# Multi-Cloud Multimodal Product Search

A full-stack application that enables users to search for products using images and/or text queries, leveraging multiple cloud AI services for comprehensive analysis and recommendations.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   MULTI-CLOUD MULTIMODAL SEARCH                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  USER INPUT                     BACKEND ORCHESTRATION           │
│  ┌──────────────┐               ┌─────────────────────────┐    │
│  │  ┌────────┐  │               │    PARALLEL EXECUTION   │    │
│  │  │  Image │  │──────────────▶│  ┌───────────────────┐  │    │
│  │  └────────┘  │  HTTP POST    │  │  Azure Vision     │  │    │
│  │              │               │  │  (GPT-4o)         │  │    │
│  │  ┌────────┐  │               │  └───────────────────┘  │    │
│  │  │  Text  │  │──────────────▶│  ┌───────────────────┐  │    │
│  │  └────────┘  │               │  │  Google Gemini    │  │    │
│  │              │               │  │  (Embeddings)     │  │    │
│  │              │               │  └───────────────────┘  │    │
│  └──────────────┘               └──────────┬──────────────┘    │
│                                             ▼                    │
│                                 ┌─────────────────────┐         │
│                                 │   LanceDB           │         │
│                                 │   Vector Search     │         │
│                                 └─────────────────────┘         │
│                                             ▼                    │
│                                 ┌─────────────────────┐         │
│                                 │   AWS Claude 3.5    │         │
│                                 │   Response Generation│         │
│                                 └─────────────────────┘         │
│                                             ▼                    │
│                                 ┌─────────────────────┐         │
│                                 │   Final JSON        │         │
│                                 │   Response          │         │
│                                 └─────────────────────┘         │
│                                             │                    │
│  USER INTERFACE                           │                    │
│  ┌───────────────────────────┐            │                    │
│  │  Similar Products Grid    │◀───────────┘                    │
│  │  with Match Explanations  │                                 │
│  └───────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Multimodal Search**: Search using images, text, or both
- **Multi-Cloud AI**: Leverages Azure GPT-4o Vision, Google Gemini, and AWS Claude 3.5
- **Vector Search**: Fast similarity search using LanceDB
- **Intelligent Recommendations**: AI-generated explanations for matches
- **Real-time Processing**: Parallel execution of AI services
- **Caching**: Redis-based caching to reduce API costs
- **Responsive UI**: Modern Next.js frontend with Tailwind CSS
- **Confidence Filtering**: Adjustable similarity thresholds
- **Brand & Price Filters**: Advanced filtering options

## Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **LanceDB**: Vector database for similarity search
- **Azure OpenAI**: GPT-4o Vision for image analysis
- **Google Gemini**: Embedding generation
- **AWS Claude 3.5**: Natural language recommendations
- **Redis**: Caching layer
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Dropzone**: Drag-and-drop file uploads

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local development environment
- **GitHub Actions**: CI/CD pipeline

## Prerequisites

Before running this application, you'll need:

1. **Azure OpenAI Account**
   - Create an Azure OpenAI resource
   - Deploy GPT-4o model
   - Get endpoint URL and API key

2. **Google AI API Key**
   - Get API key from Google AI Studio

3. **AWS Account**
   - Create IAM user with Bedrock access
   - Get access key ID and secret

4. **Python 3.11+**
5. **Node.js 18+**
6. **Docker & Docker Compose**

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MMMCsearch
```

### 2. Environment Configuration

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Google AI Configuration
GOOGLE_AI_KEY=your-google-ai-key

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1

# Redis Configuration
REDIS_URL=redis://localhost:6379

# LanceDB Configuration
LANCEDB_URI=./lancedb
```

### 3. Local Development with Docker

The easiest way to run the application is using Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000
- Redis cache
- LanceDB vector database

### 4. Manual Setup (Alternative)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Populate sample data
python sample_data.py

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## Usage

### Basic Search

1. **Image Search**: Drag and drop a product image or click to upload
2. **Text Search**: Enter a description of what you're looking for
3. **Combined Search**: Use both image and text for better results

### Advanced Features

- **Confidence Threshold**: Adjust the slider to control match strictness
- **Brand Filter**: Search within specific brands
- **Price Range**: Filter by minimum and maximum prices
- **Results**: View similarity scores and AI-generated explanations

### API Endpoints

#### Search Products
```http
POST /search
Content-Type: multipart/form-data

# Parameters:
- image: File (optional)
- text_query: string (optional)
- confidence_threshold: float (default: 0.7)
- max_results: int (default: 10)
- brand_filter: string (optional)
- price_min: float (optional)
- price_max: float (optional)
```

#### Add Products
```http
POST /products
Content-Type: application/json

{
  "products": [
    {
      "id": "prod-001",
      "name": "Sample Product",
      "brand": "Sample Brand",
      "category": "sneakers",
      "price": 99.99,
      "image_url": "https://example.com/image.jpg",
      "description": "Product description"
    }
  ]
}
```

#### Health Check
```http
GET /health
```

## Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Manual Testing

1. **Upload Test Image**: Try uploading a photo of sneakers, watches, bags, or clothing
2. **Text Queries**: Search for "red running shoes" or "luxury watch"
3. **Combined Search**: Upload an image and add text like "but in blue"
4. **Filters**: Test brand filtering and price ranges

## Deployment

### Production Deployment

#### Backend (Railway/Render)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

#### Frontend (Vercel)
1. Connect your GitHub repository
2. Vercel will auto-detect Next.js
3. Update API base URL for production

### Docker Production

```bash
# Build production images
docker build -t mmsearch-backend ./backend
docker build -t mmsearch-frontend ./frontend

# Run with production compose
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues

#### API Key Errors
- Verify all API keys are correctly set in `.env`
- Check Azure OpenAI deployment name matches your model
- Ensure AWS credentials have Bedrock permissions

#### Database Issues
- LanceDB files may need proper permissions
- Clear LanceDB directory if corrupted: `rm -rf backend/lancedb`

#### Frontend Connection
- Backend must be running on port 8000
- Check CORS settings if accessing from different domain
- Update API base URL in production

#### Memory Issues
- Large images may cause processing failures
- CLIP model requires significant RAM
- Consider using GPU for better performance

### Performance Optimization

- **Image Resizing**: Images are automatically resized before API calls
- **Caching**: Frequent queries are cached for 30 minutes
- **Parallel Processing**: All AI services run concurrently
- **Connection Pooling**: HTTP clients reuse connections

### Cost Management

- **Caching**: Reduces API calls for repeated searches
- **Confidence Thresholds**: Higher thresholds reduce false positives
- **Batch Processing**: Consider batching similar requests
- **Rate Limiting**: Built-in rate limiting prevents abuse

## Architecture Details

### Backend Modules

- **`config.py`**: Environment variable management
- **`models.py`**: Pydantic data models
- **`azure_vision.py`**: Azure GPT-4o Vision integration
- **`google_embedding.py`**: Google Gemini embedding generation
- **`aws_claude.py`**: AWS Claude recommendation engine
- **`database.py`**: LanceDB vector operations
- **`router.py`**: FastAPI route definitions
- **`cache.py`**: Redis caching utilities

### AI Service Integration

#### Azure Vision (GPT-4o)
- **Purpose**: Image analysis and feature extraction
- **Output**: Brands, colors, objects, text extraction
- **Fallback**: None (critical service)

#### Google Gemini
- **Purpose**: Vector embedding generation
- **Output**: 768-dimensional embeddings
- **Fallback**: CLIP model for local processing

#### AWS Claude 3.5
- **Purpose**: Natural language explanations
- **Output**: Personalized recommendations
- **Fallback**: Template-based responses

### Vector Search Pipeline

1. **Input Processing**: Image/text converted to embeddings
2. **Similarity Search**: Cosine similarity in LanceDB
3. **Filtering**: Confidence, brand, price filters applied
4. **Ranking**: Results sorted by similarity score
5. **Explanation**: Claude generates match explanations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Azure OpenAI for GPT-4o Vision
- Google for Gemini AI
- Amazon Web Services for Claude 3.5
- LanceDB for vector database
- Open source community for amazing tools