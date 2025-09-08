import pandas as pd
import requests
import os
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import json
from datetime import datetime
import time

# Load environment variables
load_dotenv('api_keys.env')

class OptimizedRecommendationEngine:
    def __init__(self):
        # Load data
        self.customers = pd.read_csv("data/customer.csv")
        self.catalogue = pd.read_csv("data/customer_catalogue_enhanced.csv")
        self.products = pd.read_csv("data/products.csv")
        self.sales = pd.read_csv("data/sales_enhanced.csv")
        self.stores = pd.read_csv("data/stores.csv")
        
        # Load sentence transformer model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Pre-compute product embeddings for faster cross-sell analysis
        print("🚀 Pre-computing product embeddings...")
        self.product_embeddings = {}
        for _, row in self.products.iterrows():
            product_name = row['Name']
            self.product_embeddings[product_name] = self.model.encode(product_name, convert_to_tensor=True)
        print(f"✅ Pre-computed embeddings for {len(self.product_embeddings)} products")
        
        # Cache for ingredient embeddings to avoid re-computing
        self.ingredient_cache = {}
        
        # Perplexity API configuration
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
    def query_perplexity_api(self, ingredient, product_name, catalogue_item_name, catalogue_category, catalogue_description, catalogue_ingredients):
        """Query Perplexity API to confirm if ingredient matches product"""
        if not self.perplexity_api_key:
            print(f"🔍 Potential match (API key missing): {ingredient} → {product_name}")
            return True  # Return True for testing when API key is missing
        
        # Construct the prompt for Perplexity AI
        prompt = f"""Please analyze if the product "{product_name}" from products.csv can be used as an ingredient of "{catalogue_item_name}" from customer_catalogue_enhanced.csv.

Catalogue Item Details:
- Product Name: {catalogue_item_name}
- Product Category: {catalogue_category}
- Description: {catalogue_description}
- Ingredients: {catalogue_ingredients}

Potential Ingredient: {ingredient}
Potential Product: {product_name}

Please answer with ONLY "YES" or "NO" followed by a brief reasoning (max 50 words)."""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            response = requests.post(self.perplexity_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                
                # Extract YES/NO from response
                if ai_response.upper().startswith('YES'):
                    print(f"      ✅ AI Confirmed: {ingredient} → {product_name}")
                    print(f"         AI Reasoning: {ai_response}")
                    return True, ai_response
                elif ai_response.upper().startswith('NO'):
                    print(f"      ❌ AI Rejected: {ingredient} → {product_name}")
                    print(f"         AI Reasoning: {ai_response}")
                    return False, ai_response
                else:
                    print(f"      ⚠️  AI Response unclear: {ai_response}")
                    return False, ai_response
            else:
                print(f"      ⚠️  API Error: {response.status_code} - {response.text}")
                return True, "API Error - Defaulting to True"
                
        except Exception as e:
            print(f"      ⚠️  API Exception: {str(e)}")
            return True, f"Exception: {str(e)}"
        
    def classify_customer_type(self, customer_id):
        """Classify customer type based on mathematical calculations"""
        # Get customer sales data
        cust_sales = self.sales[self.sales['CustomerID'] == customer_id]
        
        # Calculate total quantity sold
        total_quantity = cust_sales['Quantity'].sum()
        
        # Count stores from stores.csv file
        customer_stores = self.stores[self.stores['CustomerID'] == customer_id]
        number_of_stores = len(customer_stores)
        
        print(f"    📊 Customer Analysis:")
        print(f"       Total Quantity Sold: {total_quantity:,}")
        print(f"       Number of Stores: {number_of_stores}")
        
        # Classify customer based on criteria
        if number_of_stores > 50 or total_quantity > 200000:
            customer_type = "CHG Own Sales Customer"
            print(f"       Customer Type: {customer_type} (Large Scale)")
        elif (25 <= number_of_stores <= 50) or (50000 < total_quantity <= 200000):
            customer_type = "Distributor Customer"
            print(f"       Customer Type: {customer_type} (Medium Scale)")
        else:
            customer_type = "Small Customer"
            print(f"       Customer Type: {customer_type} (Small Scale)")
        
        return {
            "CustomerType": customer_type,
            "TotalQuantitySold": int(total_quantity),
            "NumberOfStores": int(number_of_stores),
            "ClassificationCriteria": {
                "StoresGreaterThan50": number_of_stores > 50,
                "QuantityGreaterThan200K": total_quantity > 200000,
                "StoresBetween25And50": 25 <= number_of_stores <= 50,
                "QuantityBetween50KAnd200K": 50000 < total_quantity <= 200000
            }
        }
    
    def get_customer_data(self, customer_id):
        """Filter data for specific customer"""
        cust_catalogue = self.catalogue[self.catalogue['CustomerID'] == customer_id]
        cust_sales = self.sales[self.sales['CustomerID'] == customer_id]
        
        # Get products that the customer has already purchased
        purchased_product_ids = cust_sales['ProductID'].unique()
        
        # Filter out products that customer has already purchased
        unsold_products = self.products[~self.products['ProductID'].isin(purchased_product_ids)]
        
        print(f"    📊 Customer has purchased {len(purchased_product_ids)} unique products")
        print(f"    🆕 {len(unsold_products)} products available for cross-sell")
        
        return cust_catalogue, cust_sales, unsold_products
    
    def analyze_up_sell(self, item_id, cust_sales, qty_required):
        """Analyze up-sell opportunities - DISABLED"""
        return []
    
    def analyze_cross_sell_optimized(self, ingredients, unsold_products, cust_sales, item_id):
        """Optimized cross-sell analysis with caching and purchase verification"""
        cross_sell_items = []
        rejected_items = []
        already_purchased_items = []
        
        # Process ingredients - split by comma and clean each ingredient
        processed_ingredients = []
        for ingredient_list in ingredients:
            ingredient_parts = ingredient_list.split(',')
            for part in ingredient_parts:
                cleaned_ingredient = part.strip()
                if cleaned_ingredient and cleaned_ingredient.lower() not in ['water', 'salt', 'sugar']:
                    processed_ingredients.append(cleaned_ingredient)
        
        if not processed_ingredients:
            return cross_sell_items, rejected_items, already_purchased_items
            
        print(f"    🔍 Processing {len(processed_ingredients)} ingredients: {processed_ingredients}")
        
        # Get list of products customer has already purchased for verification
        purchased_product_ids = cust_sales['ProductID'].unique()
        
        # Process each ingredient with caching
        for ingredient in processed_ingredients:
            print(f"    🔍 Checking ingredient: '{ingredient}'")
            
            # Get or compute ingredient embedding
            if ingredient in self.ingredient_cache:
                ingredient_embedding = self.ingredient_cache[ingredient]
            else:
                ingredient_embedding = self.model.encode(ingredient, convert_to_tensor=True)
                self.ingredient_cache[ingredient] = ingredient_embedding
            
            # Compare with all products using pre-computed embeddings
            for product_name, product_embedding in self.product_embeddings.items():
                similarity = util.cos_sim(ingredient_embedding, product_embedding).item()
                
                if similarity > 0.7:
                    print(f"      🎯 Match found: '{ingredient}' → '{product_name}' (Sim: {similarity:.3f})")
                    
                    # Get catalogue item details for confirmation
                    catalogue_item_details = self.catalogue[self.catalogue['CustomerCatalogueItemID'] == item_id]
                    if not catalogue_item_details.empty:
                        catalogue_item_name = catalogue_item_details['ProductName'].iloc[0]
                        catalogue_category = catalogue_item_details['Product Category'].iloc[0]
                        catalogue_description = catalogue_item_details['Description'].iloc[0]
                        catalogue_ingredients = catalogue_item_details['Ingredients'].iloc[0]
                        
                        confirmed, reasoning = self.query_perplexity_api(ingredient, product_name, catalogue_item_name, catalogue_category, catalogue_description, catalogue_ingredients)
                        
                        if confirmed:
                            prod_row = self.products[self.products['Name'] == product_name].iloc[0]
                            product_id = prod_row['ProductID']
                            
                            # Verify that customer hasn't already purchased this product
                            if product_id not in purchased_product_ids:
                                print(f"        ✅ Verified: Customer hasn't purchased {product_name} (ID: {product_id})")
                                cross_sell_items.append({
                                    "Ingredient": ingredient,
                                    "SuggestedProduct": product_name,
                                    "ProductID": product_id,
                                    "Similarity": round(similarity, 3),
                                    "Category": prod_row['Category'],
                                    "Price": prod_row['Price'],
                                    "AIReasoning": reasoning,
                                    "Status": "Accepted"
                                })
                            else:
                                print(f"        ❌ Skipped: Customer has already purchased {product_name} (ID: {product_id})")
                                # Add to already purchased items
                                already_purchased_items.append({
                                    "Ingredient": ingredient,
                                    "SuggestedProduct": product_name,
                                    "ProductID": product_id,
                                    "Similarity": round(similarity, 3),
                                    "Category": prod_row['Category'],
                                    "Price": prod_row['Price'],
                                    "AIReasoning": reasoning,
                                    "Status": "Already Purchased"
                                })
                        else:
                            print(f"        ❌ Rejected by AI: {ingredient} → {product_name} (Reason: {reasoning})")
                            # Add to rejected items
                            prod_row = self.products[self.products['Name'] == product_name].iloc[0]
                            rejected_items.append({
                                "Ingredient": ingredient,
                                "SuggestedProduct": product_name,
                                "ProductID": prod_row['ProductID'],
                                "Similarity": round(similarity, 3),
                                "Category": prod_row['Category'],
                                "Price": prod_row['Price'],
                                "AIReasoning": reasoning,
                                "Status": "Rejected"
                            })
        
        return cross_sell_items, rejected_items, already_purchased_items
    
    def generate_recommendations(self, customer_id):
        """Generate comprehensive recommendations for a customer"""
        print(f"\n🔍 Analyzing recommendations for CustomerID: {customer_id}")
        
        # Get customer info
        customer_info = self.customers[self.customers['CustomerID'] == customer_id]
        if customer_info.empty:
            print(f"❌ Customer {customer_id} not found!")
            return [], [], [], {}
        
        customer_name = customer_info['CustomerName'].iloc[0]
        print(f"📊 Customer: {customer_name}")
        
        # Store customer info for later use
        self.current_customer_name = customer_name
        self.current_customer_id = customer_id
        
        # Classify customer type
        customer_classification = self.classify_customer_type(customer_id)
        
        # Get customer-specific data
        cust_catalogue, cust_sales, unsold_products = self.get_customer_data(customer_id)
        
        if cust_catalogue.empty:
            print(f"❌ No catalogue items found for customer {customer_id}")
            return [], [], [], customer_classification
        
        print(f"📋 Found {len(cust_catalogue)} catalogue items")
        print(f"🆕 {len(unsold_products)} products available for cross-sell")
        
        recommendations = []
        rejected_recommendations = []
        already_purchased_recommendations = []
        items_with_recommendations = 0
        
        for _, row in cust_catalogue.iterrows():
            item_id = row['CustomerCatalogueItemID']
            item_name = row.get('ProductName', 'Unnamed Product')
            qty_required = row['QuantityRequired']
            ingredients = str(row['Ingredients']).split(";")
            
            print(f"\n🔍 Analyzing: {item_name} (ID: {item_id})")
            
            # Up-sell analysis (disabled)
            up_sell_items = self.analyze_up_sell(item_id, cust_sales, qty_required)
            
            # Cross-sell analysis (optimized)
            cross_sell_items, rejected_items, already_purchased_items = self.analyze_cross_sell_optimized(ingredients, unsold_products, cust_sales, item_id)
            
            # Add to recommendations if there are actual recommendations
            if up_sell_items or cross_sell_items:
                recommendation = {
                    "CustomerCatalogueItemID": item_id,
                    "ProductName": item_name,
                    "QuantityRequired": qty_required,
                    "Ingredients": ingredients
                }
                
                if up_sell_items:
                    recommendation["UpSell"] = up_sell_items
                
                if cross_sell_items:
                    recommendation["CrossSell"] = cross_sell_items
                
                recommendations.append(recommendation)
                items_with_recommendations += 1
            
            # Add rejected items to separate list
            if rejected_items:
                rejected_recommendation = {
                    "CustomerCatalogueItemID": item_id,
                    "ProductName": item_name,
                    "QuantityRequired": qty_required,
                    "Ingredients": ingredients,
                    "RejectedCrossSell": rejected_items
                }
                rejected_recommendations.append(rejected_recommendation)
            
            # Add already purchased items to separate list
            if already_purchased_items:
                already_purchased_recommendation = {
                    "CustomerCatalogueItemID": item_id,
                    "ProductName": item_name,
                    "QuantityRequired": qty_required,
                    "Ingredients": ingredients,
                    "AlreadyPurchasedCrossSell": already_purchased_items
                }
                already_purchased_recommendations.append(already_purchased_recommendation)
        
        print(f"✅ Found recommendations for {items_with_recommendations} out of {len(cust_catalogue)} catalogue items")
        print(f"❌ Found {len(rejected_recommendations)} items with rejected cross-sell opportunities")
        print(f"🔄 Found {len(already_purchased_recommendations)} items with already purchased cross-sell opportunities")
        return recommendations, rejected_recommendations, already_purchased_recommendations, customer_classification
    
    def display_recommendations(self, recommendations, rejected_recommendations, already_purchased_recommendations, customer_id, customer_classification=None):
        """Display formatted recommendations"""
        print(f"\n{'='*80}")
        print(f"📈 RECOMMENDATION REPORT")
        print(f"{'='*80}")
        
        if not recommendations and not rejected_recommendations and not already_purchased_recommendations:
            print("❌ No recommendations found")
            return
        
        total_up_sell = 0
        total_cross_sell = 0
        
        for rec in recommendations:
            print(f"\n🧾 Catalogue Item: {rec['ProductName']}")
            print(f"   ID: {rec['CustomerCatalogueItemID']}")
            print(f"   Required Quantity: {rec['QuantityRequired']}")
            
            # Up-sell recommendations
            if 'UpSell' in rec and rec['UpSell']:
                print(f"   ✅ Up-Sell Opportunities ({len(rec['UpSell'])}):")
                for upsell in rec['UpSell']:
                    print(f"      • {upsell['ProductName']} (ID: {upsell['ProductID']})")
                    total_up_sell += 1
            else:
                print(f"   ✅ No up-sell opportunities")
            
            # Cross-sell recommendations
            if 'CrossSell' in rec and rec['CrossSell']:
                print(f"   🔁 Cross-Sell Opportunities ({len(rec['CrossSell'])}):")
                for cross in rec['CrossSell']:
                    print(f"      • {cross['Ingredient']} → {cross['SuggestedProduct']}")
                    print(f"        Product ID: {cross['ProductID']}")
                    print(f"        Category: {cross['Category']}")
                    print(f"        Price: ${cross['Price']}")
                    print(f"        Similarity Score: {cross['Similarity']}")
                    if 'AIReasoning' in cross:
                        print(f"        AI Reasoning: {cross['AIReasoning']}")
                    total_cross_sell += 1
            else:
                print(f"   🔁 No cross-sell opportunities")
        
        # Display rejected recommendations
        if rejected_recommendations:
            print(f"\n{'='*80}")
            print(f"❌ REJECTED RECOMMENDATIONS")
            print(f"{'='*80}")
            
            total_rejected = 0
            for rec in rejected_recommendations:
                print(f"\n🧾 Catalogue Item: {rec['ProductName']}")
                print(f"   ID: {rec['CustomerCatalogueItemID']}")
                print(f"   Required Quantity: {rec['QuantityRequired']}")
                
                if 'RejectedCrossSell' in rec and rec['RejectedCrossSell']:
                    print(f"   ❌ Rejected Cross-Sell Opportunities ({len(rec['RejectedCrossSell'])}):")
                    for rejected in rec['RejectedCrossSell']:
                        print(f"      • {rejected['Ingredient']} → {rejected['SuggestedProduct']}")
                        print(f"        Product ID: {rejected['ProductID']}")
                        print(f"        Category: {rejected['Category']}")
                        print(f"        Price: ${rejected['Price']}")
                        print(f"        Similarity Score: {rejected['Similarity']}")
                        print(f"        AI Reasoning: {rejected['AIReasoning']}")
                        total_rejected += 1
        
        # Display already purchased recommendations
        if already_purchased_recommendations:
            print(f"\n{'='*80}")
            print(f"🔄 ALREADY PURCHASED RECOMMENDATIONS")
            print(f"{'='*80}")
            
            total_already_purchased = 0
            for rec in already_purchased_recommendations:
                print(f"\n🧾 Catalogue Item: {rec['ProductName']}")
                print(f"   ID: {rec['CustomerCatalogueItemID']}")
                print(f"   Required Quantity: {rec['QuantityRequired']}")
                
                if 'AlreadyPurchasedCrossSell' in rec and rec['AlreadyPurchasedCrossSell']:
                    print(f"   🔄 Already Purchased Cross-Sell Opportunities ({len(rec['AlreadyPurchasedCrossSell'])}):")
                    for already_purchased in rec['AlreadyPurchasedCrossSell']:
                        print(f"      • {already_purchased['Ingredient']} → {already_purchased['SuggestedProduct']}")
                        print(f"        Product ID: {already_purchased['ProductID']}")
                        print(f"        Category: {already_purchased['Category']}")
                        print(f"        Price: ${already_purchased['Price']}")
                        print(f"        Similarity Score: {already_purchased['Similarity']}")
                        print(f"        AI Reasoning: {already_purchased['AIReasoning']}")
                        total_already_purchased += 1
        
        print(f"\n{'='*80}")
        print(f"📊 SUMMARY")
        print(f"{'='*80}")
        print(f"Total Up-Sell Opportunities: {total_up_sell}")
        print(f"Total Cross-Sell Opportunities: {total_cross_sell}")
        print(f"Total Rejected Cross-Sell Opportunities: {total_rejected}")
        print(f"Total Already Purchased Cross-Sell Opportunities: {total_already_purchased}")
        print(f"Total Recommendations: {total_up_sell + total_cross_sell}")
        print(f"Total Rejected: {total_rejected}")
        print(f"Total Already Purchased: {total_already_purchased}")
        
        # Save recommendations to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recommendations/recommendations_{customer_id}_{timestamp}.json"
        
        # Combine accepted, rejected, and already purchased recommendations
        all_recommendations = {
            "CustomerInfo": {
                "CustomerID": self.current_customer_id,
                "CustomerName": self.current_customer_name
            },
            "CustomerClassification": customer_classification,
            "AcceptedRecommendations": recommendations,
            "RejectedRecommendations": rejected_recommendations,
            "AlreadyPurchasedRecommendations": already_purchased_recommendations,
            "Summary": {
                "TotalUpSell": total_up_sell,
                "TotalCrossSell": total_cross_sell,
                "TotalRejected": total_rejected,
                "TotalAlreadyPurchased": total_already_purchased,
                "TotalRecommendations": total_up_sell + total_cross_sell
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(all_recommendations, f, indent=2, default=str)
        
        print(f"\n💾 Recommendations saved to: {filename}")
        
        # Generate PDF report automatically
        try:
            from pdf_report_generator import PDFReportGenerator
            generator = PDFReportGenerator()
            pdf_filename = f"reports/analysis_report_{customer_id}_{timestamp}.pdf"
            success = generator.generate_pdf_report(filename, pdf_filename)
            
            if success:
                print(f"📄 PDF analysis report generated: {pdf_filename}")
            else:
                print("❌ Failed to generate PDF report")
        except ImportError:
            print("⚠️  PDF report generation skipped (pdf_report_generator.py not found)")
        except Exception as e:
            print(f"❌ Error generating PDF report: {str(e)}")

def main():
    """Main function to run the optimized recommendation engine"""
    engine = OptimizedRecommendationEngine()
    
    print("🚀 Optimized Customer Recommendation Engine")
    print("="*50)
    
    # Display available customers
    print("\n📋 Available Customers:")
    for _, customer in engine.customers.iterrows():
        print(f"   {customer['CustomerID']}: {customer['CustomerName']} ({customer['CustomerType']})")
    
    # Get customer ID from user
    customer_id = input("\nEnter CustomerID: ").strip().upper()
    
    # Generate and display recommendations
    result = engine.generate_recommendations(customer_id)
    
    if result is None:
        print("❌ Error generating recommendations.")
        return
    
    recommendations, rejected_recommendations, already_purchased_recommendations, customer_classification = result
    
    if recommendations or rejected_recommendations or already_purchased_recommendations:
        engine.display_recommendations(recommendations, rejected_recommendations, already_purchased_recommendations, customer_id, customer_classification)
    else:
        print("❌ No recommendations generated.")

if __name__ == "__main__":
    main() 