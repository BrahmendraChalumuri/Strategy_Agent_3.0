# Strategy Agent 3.0

An intelligent agent that generates cross-sell and upsell recommendations for customers using Perplexity AI. Now available as both a command-line tool and a REST API with Swagger documentation.

## Features

- **Cross-sell Recommendations**: Analyzes ingredients from customer catalogue items to find complementary products
- **Upsell Recommendations**: Identifies opportunities to increase sales based on quantity gaps
- **AI-Powered Analysis**: Uses Perplexity AI for intelligent product matching and strategy generation
- **Comprehensive Reporting**: Generates detailed recommendations with reasoning and revenue estimates
- **REST API**: FastAPI-based API with Swagger documentation
- **PDF Reports**: Automatic PDF report generation
- **Customer Classification**: Automatic customer type classification based on sales volume and store count

## Data Structure

The agent works with the following enhanced data structure:

### Customer Catalogue Enhanced (`customer_catalogue_enhanced.csv`)
- `CustomerCatalogueItemID`: Unique identifier for each catalogue item
- `CustomerID`: Customer identifier
- `ProductName`: Name of the product
- `Product Category`: Product category
- `Description`: Product description
- `Ingredients`: Product ingredients (used for cross-sell analysis)
- `ItemID`: Product ID linking to sales data
- `QuantityRequired`: Required quantity for the customer

### Sales Enhanced (`sales_enhanced.csv`)
- All original sales fields plus:
- `CustomerCatalogueItemID`: Links to customer catalogue items

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Perplexity AI API key:
```bash
export PERPLEXITY_API_KEY="your-api-key-here"
```

Or create a `api_keys.env` file:
```
PERPLEXITY_API_KEY=your-api-key-here
```

## Usage

### Command Line Interface

Run the recommendation engine:
```bash
python main.py
```

The agent will:
1. Prompt you to enter a Customer ID (C001, C002, or C003)
2. Analyze all catalogue items for that customer
3. Generate cross-sell recommendations based on ingredient matching
4. Generate upsell recommendations based on quantity gaps
5. Display results and save to a JSON file
6. Generate a PDF report automatically

### REST API

Start the API server:
```bash
python api_endpoint.py
```

The API will be available at:
- **API Documentation**: http://localhost:8001/docs
- **ReDoc Documentation**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

#### API Endpoints

**POST** `/generate-recommendations`
- Generates recommendations for a customer
- Returns complete recommendations data as JSON
- Automatically generates PDF report
- Customer IDs: C001, C002, C003

**GET** `/recommendations/{customer_id}/json`
- Retrieves recommendations in JSON format
- Returns the complete recommendations data

**GET** `/recommendations/{customer_id}/download`
- Downloads the PDF report for a customer
- Returns the PDF file for download

**GET** `/customers`
- Lists all available customers and their information

**GET** `/health`
- Health check endpoint

#### Example API Usage

Generate recommendations:
```bash
curl -X POST "http://localhost:8001/generate-recommendations" \
     -H "Content-Type: application/json" \
     -d '{"customer_id": "C001"}'
```

Get JSON recommendations:
```bash
curl -X GET "http://localhost:8001/recommendations/C001/json"
```

Download PDF report:
```bash
curl -X GET "http://localhost:8001/recommendations/C001/download" \
     --output report.pdf
```

## How It Works

### Cross-Sell Analysis
- Analyzes ingredients from customer catalogue items
- Matches with products in the same category/subcategory
- Identifies complementary products that would be consumed together
- Uses Perplexity AI to understand product relationships

### Upsell Analysis
- Compares sold quantities with required quantities
- Identifies quantity gaps where customers haven't met their requirements
- Generates strategies like quantity increases, bundles, premium versions
- Calculates estimated revenue from upsell opportunities

### Output Format

The agent generates recommendations in this structure:
```json
{
  "success": true,
  "message": "Recommendations generated successfully for customer C001",
  "customer_id": "C001",
  "timestamp": "20240908_130005",
  "CustomerInfo": {
    "CustomerID": "C001",
    "CustomerName": "Starbucks"
  },
  "CustomerClassification": {
    "CustomerType": "CHG Own Sales Customer",
    "TotalQuantitySold": 1000,
    "NumberOfStores": 99,
    "ClassificationCriteria": {
      "StoresGreaterThan50": true,
      "QuantityGreaterThan200K": false
    }
  },
  "AcceptedRecommendations": [
    {
      "CustomerCatalogueItemID": "CC101",
      "ProductName": "Starbucks® Chocolate Chip Cookie",
      "QuantityRequired": 800,
      "Ingredients": ["Biscuit Dough", "Chocolate chips", "Vanilla extract", "Eggs", "Butter"],
      "CrossSell": [
        {
          "Ingredient": "Biscuit Dough",
          "SuggestedProduct": "Pioneer® Simple Split Biscuit Dough",
          "ProductID": 210101,
          "Similarity": 0.723,
          "Category": "Biscuits",
          "Price": 34.8,
          "AIReasoning": "YES. Pioneer® Simple Split Biscuit Dough is a versatile biscuit dough...",
          "Status": "Accepted"
        }
      ]
    }
  ],
  "RejectedRecommendations": [
    {
      "CustomerCatalogueItemID": "CC101",
      "ProductName": "Starbucks® Chocolate Chip Cookie",
      "QuantityRequired": 800,
      "Ingredients": ["Biscuit Dough", "Chocolate chips", "Vanilla extract", "Eggs", "Butter"],
      "RejectedCrossSell": [
        {
          "Ingredient": "Biscuit Dough",
          "SuggestedProduct": "Pioneer® Southern Style Biscuit Dough",
          "ProductID": 8095,
          "Similarity": 0.742,
          "Category": "Biscuits",
          "Price": 31.2,
          "AIReasoning": "NO. Pioneer® Southern Style Biscuit Dough is designed for biscuits rather than cookie dough...",
          "Status": "Rejected"
        }
      ]
    }
  ],
  "AlreadyPurchasedRecommendations": [
    {
      "CustomerCatalogueItemID": "CC103",
      "ProductName": "Starbucks® Buttermilk Biscuit",
      "QuantityRequired": 400,
      "Ingredients": ["Biscuit Dough", "Buttermilk", "Butter"],
      "AlreadyPurchasedCrossSell": [
        {
          "Ingredient": "Biscuit Dough",
          "SuggestedProduct": "Pioneer® Southern Style Biscuit Dough",
          "ProductID": 8095,
          "Similarity": 0.742,
          "Category": "Biscuits",
          "Price": 31.2,
          "AIReasoning": "YES. Pioneer® Southern Style Biscuit Dough contains key ingredients...",
          "Status": "Already Purchased"
        }
      ]
    }
  ],
  "Summary": {
    "TotalUpSell": 0,
    "TotalCrossSell": 20,
    "TotalRejected": 12,
    "TotalAlreadyPurchased": 1,
    "TotalRecommendations": 20
  },
  "files_generated": {
    "json_file": "recommendations/recommendations_C001_20240908_130005.json",
    "pdf_file": "reports/analysis_report_C001_20240908_130005.pdf"
  }
}
```

## Example Output

### Command Line Output
```
🎯 RECOMMENDATIONS FOR CUSTOMER C001
📊 Analyzed 32 items, found recommendations for 7 items
⏰ Generated at: 2024-09-08T13:00:05
================================================================================

📦 Starbucks® Chocolate Chip Cookie (ID: CC101)
   Category: Cookies | Required Qty: 800
   🔄 CROSS-SELL OPPORTUNITIES (3):
      1. Pioneer® Simple Split Biscuit Dough ($34.80)
         Category: Biscuits | Similarity: 0.723
         AI Reasoning: YES. Pioneer® Simple Split Biscuit Dough is a versatile biscuit dough...
      2. Conestoga™ Simple Split Whole Grain Biscuit Dough ($31.20)
         Category: Biscuits | Similarity: 0.745
         AI Reasoning: YES. The Conestoga™ Simple Split Whole Grain Biscuit Dough...
      3. Conestoga™ Simple Split Homestyle Biscuit Dough ($36.60)
         Category: Biscuits | Similarity: 0.731
         AI Reasoning: YES. The Conestoga™ Simple Split Homestyle Biscuit Dough...

📊 SUMMARY
Total Cross-Sell Opportunities: 20
Total Rejected Cross-Sell Opportunities: 12
Total Already Purchased Cross-Sell Opportunities: 1
```

### API Response Example
```json
{
  "success": true,
  "message": "Recommendations generated successfully for customer C001",
  "customer_id": "C001",
  "timestamp": "20240908_130005",
  "CustomerInfo": {
    "CustomerID": "C001",
    "CustomerName": "Starbucks"
  },
  "CustomerClassification": {
    "CustomerType": "CHG Own Sales Customer",
    "TotalQuantitySold": 1000,
    "NumberOfStores": 99
  },
  "Summary": {
    "TotalCrossSell": 20,
    "TotalRejected": 12,
    "TotalAlreadyPurchased": 1,
    "TotalRecommendations": 20
  },
  "files_generated": {
    "json_file": "recommendations/recommendations_C001_20240908_130005.json",
    "pdf_file": "reports/analysis_report_C001_20240908_130005.pdf"
  }
}
```

## Project Structure

```
Strategy_Agent_3.0/
├── data/                    # Data files
│   ├── customer.csv
│   ├── customer_catalogue_enhanced.csv
│   ├── sales_enhanced.csv
│   ├── products.csv
│   ├── stores.csv
│   └── plants.csv
├── recommendations/         # Generated JSON recommendations
│   └── recommendations_*.json
├── reports/                # Generated PDF reports
│   └── analysis_report_*.pdf
├── main.py                 # Main recommendation engine (CLI)
├── api_endpoint.py         # FastAPI REST API server
├── pdf_report_generator.py # PDF report generator
├── test_api.py            # API testing script
├── requirements.txt        # Python dependencies
├── api_keys.env           # API keys configuration
└── README.md              # Documentation
```

## Files

- `main.py`: Main recommendation engine (command-line interface)
- `api_endpoint.py`: FastAPI REST API server with Swagger documentation
- `pdf_report_generator.py`: PDF report generator
- `test_api.py`: API testing script
- `data/customer_catalogue_enhanced.csv`: Enhanced customer catalogue with ItemID and QuantityRequired
- `data/sales_enhanced.csv`: Enhanced sales data with CustomerCatalogueItemID
- `data/products.csv`: Product catalog with categories and subcategories
- `requirements.txt`: Python dependencies (includes FastAPI, uvicorn, pydantic)
- `api_keys.env`: API keys configuration
- `README.md`: This documentation

## Customer Classification

The system automatically classifies customers based on sales volume and store count:

- **CHG Own Sales Customer**: >50 stores OR >200,000 total quantity sold
- **Distributor Customer**: 25-50 stores OR 50,000-200,000 total quantity sold  
- **Small Customer**: <25 stores AND <50,000 total quantity sold

## AI-Powered Analysis

- **Sentence Transformers**: Uses `all-MiniLM-L6-v2` model for semantic similarity matching
- **Perplexity AI**: Validates ingredient-product relationships with reasoning
- **Similarity Threshold**: 0.7+ similarity score for cross-sell recommendations
- **Purchase Verification**: Excludes products customer has already purchased

## Notes

- The agent skips items where no cross-sell or upsell opportunities are found
- Cross-sell analysis requires ingredients data to be available
- Upsell analysis is currently disabled (can be enabled in the code)
- All recommendations are generated using Perplexity AI for intelligent analysis
- PDF reports are automatically generated for both CLI and API usage
- API runs on port 8001 by default (configurable in `api_endpoint.py`)
- Swagger documentation is available at `/docs` endpoint 