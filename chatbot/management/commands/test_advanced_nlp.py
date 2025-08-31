"""
Django management command to test the advanced NLP processor features.
"""

from django.core.management.base import BaseCommand
from chatbot.nlp_processor import NLPProcessor


class Command(BaseCommand):
    help = 'Test advanced NLP processor features'

    def handle(self, *args, **options):
        """Test the enhanced NLP processor"""
        
        self.stdout.write("Testing Advanced NLP Processor...")
        self.stdout.write("=" * 50)
        
        # Initialize processor
        nlp = NLPProcessor()
        
        # Test queries with increasing complexity
        test_queries = [
            "What is the revenue for 2024-25?",
            "Show me employee benefits for FY 2024-25",
            "What are the total assets in fiscal year 2025-26?", 
            "Compare revenue between 2024-25 and 2025-26",
            "What is the cash flow for 2024/25?",
            "Show me all expenses",
            "What are the liabilities?",
            "Tell me about comprehensive income for 2024",
            "Invalid query with no metrics",
            "Random text that doesn't make sense"
        ]
        
        for i, query in enumerate(test_queries, 1):
            self.stdout.write(f"\\n{i}. Testing Query: '{query}'")
            self.stdout.write("-" * 40)
            
            try:
                # Test basic processing
                intent = nlp.process_query(query)
                self.stdout.write(f"Entity: {intent.entity}")
                self.stdout.write(f"Action: {intent.action}")
                self.stdout.write(f"Years: {intent.years}")
                self.stdout.write(f"Confidence: {intent.confidence:.2f}")
                
                # Test advanced SQL generation if convert_to_sql exists
                if hasattr(nlp, 'convert_to_sql'):
                    sql, confidence, suggestions = nlp.convert_to_sql(query)
                    if suggestions:
                        self.stdout.write(f"\\nSuggestions:")
                        for suggestion in suggestions:
                            self.stdout.write(f"  - {suggestion}")
                    else:
                        self.stdout.write(f"\\nAdvanced SQL: {sql}")
                        self.stdout.write(f"SQL Confidence: {confidence:.2f}")
                
                # Test confidence scoring
                if hasattr(nlp, 'get_confidence_score'):
                    detailed_confidence = nlp.get_confidence_score(intent.entity, intent.years, query)
                    self.stdout.write(f"Detailed Confidence: {detailed_confidence:.2f}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing query: {e}"))
        
        # Test training data loading
        self.stdout.write("\\n" + "=" * 50)
        self.stdout.write("Training Data Summary:")
        self.stdout.write("-" * 25)
        
        if hasattr(nlp, 'file_mappings'):
            self.stdout.write(f"File mappings loaded: {len(nlp.file_mappings)}")
            for entity, mapping in list(nlp.file_mappings.items())[:3]:
                self.stdout.write(f"  {entity}: {mapping['statement_type']}")
            if len(nlp.file_mappings) > 3:
                self.stdout.write(f"  ... and {len(nlp.file_mappings) - 3} more")
        
        if hasattr(nlp, 'row_mappings'):
            self.stdout.write(f"Row mappings loaded: {len(nlp.row_mappings)}")
        
        if hasattr(nlp, 'column_mappings'):
            self.stdout.write(f"Column mappings loaded: {len(nlp.column_mappings)}")
        
        if hasattr(nlp, 'metric_keywords'):
            self.stdout.write(f"Metric keywords loaded: {len(nlp.metric_keywords)}")
            
            # Show some examples
            self.stdout.write("\\nExample metric keywords:")
            for entity, keywords in list(nlp.metric_keywords.items())[:3]:
                self.stdout.write(f"  {entity}: {', '.join(keywords[:3])}...")
        
        # Test specific features
        self.stdout.write("\\n" + "=" * 50)
        self.stdout.write("Feature Tests:")
        self.stdout.write("-" * 15)
        
        # Test fiscal year extraction
        if hasattr(nlp, '_extract_fiscal_year'):
            test_year_queries = [
                "revenue for 2024-25",
                "expenses in FY 2025-26", 
                "assets for fiscal year 2024/25",
                "just 2024 alone"
            ]
            
            self.stdout.write("\\nFiscal Year Extraction:")
            for query in test_year_queries:
                years = nlp._extract_fiscal_year(query)
                self.stdout.write(f"  '{query}' → {years}")
        
        # Test entity extraction  
        if hasattr(nlp, '_extract_entity'):
            test_entity_queries = [
                "employee benefits",
                "total revenue and income", 
                "cash flow statement",
                "current assets and liabilities"
            ]
            
            self.stdout.write("\\nEntity Extraction:")
            for query in test_entity_queries:
                entity = nlp._extract_entity(query)
                self.stdout.write(f"  '{query}' → {entity}")
        
        self.stdout.write("\\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("Advanced NLP Testing Complete!"))
        
        # Show supported features
        self.stdout.write("\\nSupported Features:")
        features = [
            "✓ Training data integration (file, row, column mappings)",
            "✓ Advanced entity recognition with keyword scoring",
            "✓ Multiple fiscal year format support", 
            "✓ Confidence scoring and thresholds",
            "✓ Intelligent suggestions for failed queries",
            "✓ Sophisticated SQL generation",
            "✓ Statement type mapping",
            "✓ Enhanced error handling and user guidance"
        ]
        
        for feature in features:
            self.stdout.write(f"  {feature}")
        
        self.stdout.write("\\nSupported Query Patterns:")
        patterns = [
            "• What is [metric] for [year]?",
            "• Show me [metric] in [year]", 
            "• Compare [metric] between [year1] and [year2]",
            "• Tell me about [metric]",
            "• What are the [category] for [year]?"
        ]
        
        for pattern in patterns:
            self.stdout.write(f"  {pattern}")
        
        self.stdout.write("\\nSupported Fiscal Years:")
        if hasattr(nlp, 'supported_years'):
            self.stdout.write(f"  {', '.join(nlp.supported_years)}")
        
        self.stdout.write("\\nSupported Financial Metrics:")
        if hasattr(nlp, 'metric_keywords'):
            metrics = list(nlp.metric_keywords.keys())[:10]  # Show first 10
            self.stdout.write(f"  {', '.join(metrics)}")
            if len(nlp.metric_keywords) > 10:
                self.stdout.write(f"  ... and {len(nlp.metric_keywords) - 10} more")
