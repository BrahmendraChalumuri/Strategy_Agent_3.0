# Customer Recommendation Agent

An intelligent agent that generates cross-sell and upsell recommendations for customers using Perplexity AI.

## Features

- **Cross-sell Recommendations**: Analyzes ingredients from customer catalogue items to find complementary products
- **Upsell Recommendations**: Identifies opportunities to increase sales based on quantity gaps
- **AI-Powered Analysis**: Uses Perplexity AI for intelligent product matching and strategy generation
- **Comprehensive Reporting**: Generates detailed recommendations with reasoning and revenue estimates

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

Or create a `.env` file:
```
PERPLEXITY_API_KEY=your-api-key-here
```

## Usage

Run the recommendation engine:
```bash
python test2_optimized.py
```

The agent will:
1. Prompt you to enter a Customer ID (C001, C002, or C003)
2. Analyze all catalogue items for that customer
3. Generate cross-sell recommendations based on ingredient matching
4. Generate upsell recommendations based on quantity gaps
5. Display results and save to a JSON file

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
  "customer_id": "C001",
  "timestamp": "2024-01-15T10:30:00",
  "total_items_analyzed": 25,
  "items_with_recommendations": 15,
  "recommendations": [
    {
      "catalogue_item_id": "CC001",
      "product_name": "Cool Lime Starbucks Refreshers™ Beverage",
      "category": "Refreshers",
      "item_id": "8095",
      "quantity_required": 500,
      "cross_sell": [
        {
          "product_id": "1234",
          "product_name": "Complementary Product",
          "category": "Beverages",
          "subcategory": "Juices",
          "price": 15.99,
          "reasoning": "This product complements the original beverage..."
        }
      ],
      "upsell": [
        {
          "upsell_type": "quantity_increase",
          "recommended_quantity": 750,
          "estimated_revenue": 1875.00,
          "reasoning": "Customer has only purchased 300 units but requires 500..."
        }
      ]
    }
  ]
}
```

## Example Output

```
🎯 RECOMMENDATIONS FOR CUSTOMER C001
📊 Analyzed 25 items, found recommendations for 15 items
⏰ Generated at: 2024-01-15T10:30:00
================================================================================

📦 Cool Lime Starbucks Refreshers™ Beverage (ID: CC001)
   Category: Refreshers | Required Qty: 500
   🔄 CROSS-SELL OPPORTUNITIES (2):
      1. Evolution Fresh™ Cold-Pressed Apple Berry Juice ($31.50)
         Category: Cold-Pressed Juices | Cold-Pressed Juices
         Reason: Complementary beverage that uses similar natural flavors and fruit ingredients
      2. Tazo® Bottled Berry Blossom White ($18.40)
         Category: Tea | Bottled Tea
         Reason: Light tea option that pairs well with refreshing beverages
   📈 UPSELL OPPORTUNITIES (1):
      1. Quantity Increase
         Recommended Qty: 750
         Estimated Revenue: $1875.00
         Strategy: Customer has only purchased 300 units but requires 500, suggesting a 50% increase to meet demand
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
├── test2_optimized.py      # Main recommendation engine
├── pdf_report_generator.py # PDF report generator
├── requirements.txt        # Python dependencies
├── api_keys.env           # API keys configuration
└── README.md              # Documentation
```

## Files

- `test2_optimized.py`: Main recommendation engine
- `pdf_report_generator.py`: PDF report generator
- `data/customer_catalogue_enhanced.csv`: Enhanced customer catalogue with ItemID and QuantityRequired
- `data/sales_enhanced.csv`: Enhanced sales data with CustomerCatalogueItemID
- `data/products.csv`: Product catalog with categories and subcategories
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Notes

- The agent skips items where no cross-sell or upsell opportunities are found
- Cross-sell analysis requires ingredients data to be available
- Upsell analysis only works for items that have been previously sold
- All recommendations are generated using Perplexity AI for intelligent analysis 