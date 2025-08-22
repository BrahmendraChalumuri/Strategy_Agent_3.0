import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkred
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Highlight style for important information
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkblue,
            alignment=TA_JUSTIFY
        ))
    
    def load_json_data(self, json_file_path):
        """Load JSON data from file"""
        try:
            with open(json_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ JSON file not found: {json_file_path}")
            return None
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON format in file: {json_file_path}")
            return None
    
    def generate_customer_classification_analysis(self, customer_classification, customer_info=None):
        """Generate customer classification analysis section"""
        story = []
        
        # Customer name and ID header
        if customer_info:
            customer_name = customer_info.get('CustomerName', 'Unknown Customer')
            customer_id = customer_info.get('CustomerID', 'Unknown ID')
            customer_header = f"{customer_name} ({customer_id})"
            story.append(Paragraph(customer_header, self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
        
        # Section header
        story.append(Paragraph("Customer Classification Analysis", self.styles['SectionHeader']))
        
        # Customer type analysis
        customer_type = customer_classification.get('CustomerType', 'Unknown')
        total_quantity = customer_classification.get('TotalQuantitySold', 0)
        number_of_stores = customer_classification.get('NumberOfStores', 0)
        
        # Main analysis paragraph
        analysis_text = f"""
        The customer has been classified as a <b>{customer_type}</b> based on comprehensive analysis of their business operations. 
        This classification is determined through mathematical calculations considering both the scale of their store network and 
        their purchasing volume. The customer operates <b>{number_of_stores:,} stores</b> across their network and has purchased 
        a total of <b>{total_quantity:,} units</b> of products, indicating their market presence and purchasing power.
        """
        story.append(Paragraph(analysis_text, self.styles['CustomBodyText']))
        
        # Classification criteria analysis
        criteria = customer_classification.get('ClassificationCriteria', {})
        
        criteria_text = f"""
        The classification criteria analysis reveals that this customer meets the following thresholds: 
        {'✓' if criteria.get('StoresGreaterThan50', False) else '✗'} Stores > 50, 
        {'✓' if criteria.get('QuantityGreaterThan200K', False) else '✗'} Quantity > 200,000, 
        {'✓' if criteria.get('StoresBetween25And50', False) else '✗'} Stores between 25-50, 
        {'✓' if criteria.get('QuantityBetween50KAnd200K', False) else '✗'} Quantity between 50,000-200,000.
        """
        story.append(Paragraph(criteria_text, self.styles['Highlight']))
        
        # Business implications
        implications_text = f"""
        This classification has significant implications for our cross-selling strategy. As a {customer_type.lower()}, 
        the customer represents a {'high-value' if customer_type == 'CHG Own Sales Customer' else 'medium-value' if customer_type == 'Distributor Customer' else 'developing'} 
        business relationship that requires {'premium' if customer_type == 'CHG Own Sales Customer' else 'standard' if customer_type == 'Distributor Customer' else 'basic'} 
        attention and customized recommendations. The extensive store network and substantial purchasing volume suggest 
        strong potential for implementing comprehensive cross-selling initiatives across their operations.
        """
        story.append(Paragraph(implications_text, self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 12))
        return story
    
    def generate_cross_sell_analysis(self, data):
        """Generate cross-sell analysis section"""
        story = []
        
        # Section header
        story.append(Paragraph("Cross-Sell Recommendations Analysis", self.styles['SectionHeader']))
        
        # Accepted recommendations
        accepted_recommendations = data.get('AcceptedRecommendations', [])
        if accepted_recommendations:
            story.append(Paragraph("Accepted Cross-Sell Opportunities", self.styles['SubsectionHeader']))
            
            accepted_text = f"""
            Our analysis identified <b>{len(accepted_recommendations)} catalogue items</b> with viable cross-sell opportunities 
            that have been validated through AI-powered ingredient matching and confirmed as suitable for the customer's 
            current product portfolio. These recommendations represent products that the customer has not previously 
            purchased and are deemed appropriate based on ingredient compatibility analysis.
            """
            story.append(Paragraph(accepted_text, self.styles['CustomBodyText']))
            
            # Detailed analysis of each accepted recommendation
            for rec in accepted_recommendations:
                item_name = rec.get('ProductName', 'Unknown Product')
                item_id = rec.get('CustomerCatalogueItemID', 'Unknown ID')
                cross_sell_items = rec.get('CrossSell', [])
                
                if cross_sell_items:
                    item_text = f"""
                    <b>{item_name}</b> (ID: {item_id}) presents {len(cross_sell_items)} cross-sell opportunities:
                    """
                    story.append(Paragraph(item_text, self.styles['CustomBodyText']))
                    
                    # List each cross-sell product with details
                    for i, cross_sell in enumerate(cross_sell_items, 1):
                        product_name = cross_sell.get('SuggestedProduct', 'Unknown Product')
                        product_id = cross_sell.get('ProductID', 'Unknown ID')
                        category = cross_sell.get('Category', 'Unknown Category')
                        price = cross_sell.get('Price', 0)
                        similarity = cross_sell.get('Similarity', 0)
                        reasoning = cross_sell.get('AIReasoning', 'No reasoning provided')
                        
                        cross_sell_text = f"""
                        <b>{i}.</b> <b>{product_name}</b> (ID: {product_id})
                        • Category: {category}
                        • Price: ${price}
                        • Similarity Score: {similarity:.3f}
                        • AI Reasoning: {reasoning}
                        """
                        story.append(Paragraph(cross_sell_text, self.styles['CustomBodyText']))
                        story.append(Spacer(1, 6))
        
        # Rejected recommendations
        rejected_recommendations = data.get('RejectedRecommendations', [])
        if rejected_recommendations:
            story.append(Paragraph("Rejected Cross-Sell Opportunities", self.styles['SubsectionHeader']))
            
            rejected_text = f"""
            Our AI analysis identified <b>{len(rejected_recommendations)} catalogue items</b> with potential cross-sell 
            opportunities that were ultimately rejected based on detailed ingredient compatibility analysis. 
            These rejections demonstrate the system's ability to provide accurate, validated recommendations 
            rather than simply suggesting all possible matches.
            """
            story.append(Paragraph(rejected_text, self.styles['CustomBodyText']))
            
            for rec in rejected_recommendations:
                item_name = rec.get('ProductName', 'Unknown Product')
                rejected_items = rec.get('RejectedCrossSell', [])
                
                if rejected_items:
                    item_text = f"""
                    <b>{item_name}</b> had {len(rejected_items)} potential cross-sell opportunities that were 
                    rejected by our AI analysis:
                    """
                    story.append(Paragraph(item_text, self.styles['CustomBodyText']))
                    
                    # List each rejected cross-sell product with details
                    for i, rejected in enumerate(rejected_items, 1):
                        product_name = rejected.get('SuggestedProduct', 'Unknown Product')
                        product_id = rejected.get('ProductID', 'Unknown ID')
                        category = rejected.get('Category', 'Unknown Category')
                        price = rejected.get('Price', 0)
                        similarity = rejected.get('Similarity', 0)
                        reasoning = rejected.get('AIReasoning', 'No reasoning provided')
                        
                        rejected_text = f"""
                        <b>{i}.</b> <b>{product_name}</b> (ID: {product_id})
                        • Category: {category}
                        • Price: ${price}
                        • Similarity Score: {similarity:.3f}
                        • Rejection Reason: {reasoning}
                        """
                        story.append(Paragraph(rejected_text, self.styles['CustomBodyText']))
                        story.append(Spacer(1, 6))
        
        # Already purchased recommendations
        already_purchased_recommendations = data.get('AlreadyPurchasedRecommendations', [])
        if already_purchased_recommendations:
            story.append(Paragraph("Already Purchased Cross-Sell Opportunities", self.styles['SubsectionHeader']))
            
            purchased_text = f"""
            The analysis identified <b>{len(already_purchased_recommendations)} catalogue items</b> where the customer 
            has already purchased the recommended cross-sell products. This demonstrates the system's ability 
            to track customer purchase history and avoid redundant recommendations, ensuring efficient use of 
            the customer's resources and preventing duplicate purchases.
            """
            story.append(Paragraph(purchased_text, self.styles['CustomBodyText']))
            
            # List each already purchased cross-sell product with details
            for rec in already_purchased_recommendations:
                item_name = rec.get('ProductName', 'Unknown Product')
                purchased_items = rec.get('AlreadyPurchasedCrossSell', [])
                
                if purchased_items:
                    item_text = f"""
                    <b>{item_name}</b> has {len(purchased_items)} cross-sell products already purchased:
                    """
                    story.append(Paragraph(item_text, self.styles['CustomBodyText']))
                    
                    for i, purchased in enumerate(purchased_items, 1):
                        product_name = purchased.get('SuggestedProduct', 'Unknown Product')
                        product_id = purchased.get('ProductID', 'Unknown ID')
                        category = purchased.get('Category', 'Unknown Category')
                        price = purchased.get('Price', 0)
                        similarity = purchased.get('Similarity', 0)
                        reasoning = purchased.get('AIReasoning', 'No reasoning provided')
                        
                        purchased_item_text = f"""
                        <b>{i}.</b> <b>{product_name}</b> (ID: {product_id})
                        • Category: {category}
                        • Price: ${price}
                        • Similarity Score: {similarity:.3f}
                        • AI Reasoning: {reasoning}
                        """
                        story.append(Paragraph(purchased_item_text, self.styles['CustomBodyText']))
                        story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        return story
    
    def generate_up_sell_analysis(self, data):
        """Generate up-sell analysis section"""
        story = []
        
        # Section header
        story.append(Paragraph("Up-Sell Recommendations Analysis", self.styles['SectionHeader']))
        
        accepted_recommendations = data.get('AcceptedRecommendations', [])
        up_sell_count = 0
        
        for rec in accepted_recommendations:
            up_sell_items = rec.get('UpSell', [])
            up_sell_count += len(up_sell_items)
        
        if up_sell_count > 0:
            up_sell_text = f"""
            The analysis identified <b>{up_sell_count} up-sell opportunities</b> across the customer's catalogue items. 
            These recommendations focus on encouraging the customer to purchase higher-value versions of products 
            they already use, or to increase their order quantities for existing products. Up-sell opportunities 
            are carefully evaluated to ensure they provide genuine value to the customer while supporting business growth.
            """
            story.append(Paragraph(up_sell_text, self.styles['CustomBodyText']))
        else:
            up_sell_text = """
            <b>No up-sell opportunities were identified</b> in the current analysis. This may indicate that 
            the customer is already purchasing optimal quantities of products, or that the current catalogue 
            items don't present clear up-sell scenarios. The system continues to monitor for future up-sell 
            opportunities as the customer's needs evolve.
            """
            story.append(Paragraph(up_sell_text, self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 12))
        return story
    
    def generate_summary_analysis(self, data):
        """Generate summary analysis section"""
        story = []
        
        # Section header
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        summary = data.get('Summary', {})
        total_up_sell = summary.get('TotalUpSell', 0)
        total_cross_sell = summary.get('TotalCrossSell', 0)
        total_rejected = summary.get('TotalRejected', 0)
        total_already_purchased = summary.get('TotalAlreadyPurchased', 0)
        total_recommendations = summary.get('TotalRecommendations', 0)
        
        # Overall analysis
        summary_text = f"""
        The comprehensive analysis of the customer's catalogue and purchase history has yielded significant 
        insights for cross-selling strategy development. The system processed multiple catalogue items and 
        identified <b>{total_recommendations} viable recommendations</b> across up-sell and cross-sell categories.
        """
        story.append(Paragraph(summary_text, self.styles['CustomBodyText']))
        
        # Recommendation breakdown
        breakdown_text = f"""
        The recommendation breakdown shows <b>{total_cross_sell} accepted cross-sell opportunities</b>, 
        <b>{total_rejected} rejected opportunities</b> (demonstrating quality control), and 
        <b>{total_already_purchased} already purchased items</b> (showing effective duplicate prevention). 
        Additionally, <b>{total_up_sell} up-sell opportunities</b> were identified to enhance customer value.
        """
        story.append(Paragraph(breakdown_text, self.styles['CustomBodyText']))
        
        # Strategic implications
        implications_text = f"""
        These findings provide a solid foundation for implementing targeted cross-selling initiatives. 
        The high number of accepted recommendations indicates strong potential for revenue growth, while 
        the rejection rate demonstrates the system's commitment to quality and accuracy. The identification 
        of already purchased items shows effective inventory tracking and prevents redundant recommendations.
        """
        story.append(Paragraph(implications_text, self.styles['CustomBodyText']))
        
        # Next steps
        next_steps_text = f"""
        <b>Recommended Next Steps:</b> Focus on the {total_cross_sell} accepted cross-sell opportunities 
        as priority implementation targets. These recommendations have been validated through AI analysis 
        and represent the highest probability of successful adoption by the customer. Regular monitoring 
        of these recommendations will help track implementation success and identify additional opportunities.
        """
        story.append(Paragraph(next_steps_text, self.styles['Highlight']))
        
        story.append(Spacer(1, 12))
        return story
    
    def generate_pdf_report(self, json_file_path, output_pdf_path=None):
        """Generate comprehensive PDF report from JSON data"""
        # Load JSON data
        data = self.load_json_data(json_file_path)
        if not data:
            return False
        
        # Generate output filename if not provided
        if not output_pdf_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_pdf_path = f"reports/analysis_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(output_pdf_path, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        story.append(Paragraph("Customer Recommendation Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Introduction
        intro_text = f"""
        This comprehensive analysis report provides detailed insights into cross-selling and up-selling 
        opportunities for the customer, generated through advanced AI-powered ingredient matching and 
        customer classification algorithms. The analysis was conducted on {datetime.now().strftime('%B %d, %Y')} 
        and represents the most current assessment of available opportunities.
        """
        story.append(Paragraph(intro_text, self.styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Customer Classification Analysis
        customer_classification = data.get('CustomerClassification', {})
        customer_info = data.get('CustomerInfo', {})
        if customer_classification:
            story.extend(self.generate_customer_classification_analysis(customer_classification, customer_info))
        
        # Cross-Sell Analysis
        story.extend(self.generate_cross_sell_analysis(data))
        
        # Up-Sell Analysis
        story.extend(self.generate_up_sell_analysis(data))
        
        # Summary
        story.extend(self.generate_summary_analysis(data))
        
        # Build PDF
        try:
            doc.build(story)
            print(f"✅ PDF report generated successfully: {output_pdf_path}")
            return True
        except Exception as e:
            print(f"❌ Error generating PDF report: {str(e)}")
            return False

def main():
    """Main function to generate PDF report"""
    generator = PDFReportGenerator()
    
    # Find the most recent JSON file
    json_files = [f for f in os.listdir('recommendations') if f.startswith('recommendations_') and f.endswith('.json')]
    
    if not json_files:
        print("❌ No recommendation JSON files found in current directory")
        return
    
    # Sort by modification time to get the most recent
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join('recommendations', x)), reverse=True)
    latest_json_file = os.path.join('recommendations', json_files[0])
    
    print(f"📄 Found JSON file: {latest_json_file}")
    
    # Generate PDF report
    success = generator.generate_pdf_report(latest_json_file)
    
    if success:
        print("🎉 PDF analysis report generated successfully!")
    else:
        print("❌ Failed to generate PDF report")

if __name__ == "__main__":
    main() 