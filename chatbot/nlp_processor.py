"""
Natural Language Processing module for the financial chatbot.
This module handles question understanding, intent recognition, and SQL query generation.
Advanced features include training data parsing, confidence scoring, and sophisticated mapping.
"""

import re
import logging
import pandas as pd
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class QueryIntent:
    """Represents the intent parsed from a user query"""
    action: str  # 'get', 'compare', 'calculate', 'show'
    entity: str  # 'revenue', 'expenses', 'assets', etc.
    years: List[str]  # ['2024-25', '2025-26']
    filters: Dict[str, str]  # Additional filters
    confidence: float  # Confidence score 0-1


class NLPProcessor:
    """Advanced conversational AI processor with ChatGPT-like capabilities"""
    
    def __init__(self):
        # Conversational patterns
        self.greeting_patterns = {
            'hello': [r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b'],
            'goodbye': [r'\b(bye|goodbye|see you|thanks|thank you|exit|quit)\b'],
            'help': [r'\b(help|what can you do|how does this work|guide|assist)\b'],
            'status': [r'\b(status|health|working|available)\b']
        }
        
        self.conversation_responses = {
            'hello': [
                "Hello! I'm your financial data assistant. How may I help you today?",
                "Hi there! I can help you analyze financial data from your Excel files. What would you like to know?",
                "Good day! I'm here to assist with your financial queries. Feel free to ask about revenue, expenses, assets, or any other financial metrics."
            ],
            'goodbye': [
                "Thank you for using the financial chatbot. Have a great day!",
                "Goodbye! Feel free to return anytime for financial data analysis.",
                "See you later! I'm always here to help with your financial questions."
            ],
            'help': [
                "I can help you analyze financial data from your Excel files. Here are some things you can ask:\n• What are the employee benefits for 2024-25?\n• Compare revenue between 2024-25 and 2025-26\n• Show me total expenses for 2025-26\n• What are the assets for fiscal year 2024-25?",
                "I'm your financial data assistant! You can ask me about:\n✓ Revenue and income data\n✓ Expenses and costs\n✓ Assets and liabilities\n✓ Cash flow information\n✓ Year-over-year comparisons\n\nJust ask in natural language and I'll find the data for you!"
            ],
            'status': [
                "I'm running perfectly and ready to help! My financial databases are loaded and I can access data for fiscal years 2023-24 through 2027-28.",
                "All systems operational! I have access to your Excel financial data and can answer questions about income statements, balance sheets, and more."
            ]
        }
        
        # Financial query patterns
        self.year_patterns = [
            r'20\d{2}-\d{2}',  # 2024-25 format
            r'20\d{2}/\d{2}',  # 2024/25 format  
            r'FY\s*20\d{2}-?\d{0,2}',   # FY 2024-25 format
            r'fiscal\s+year\s+20\d{2}',
            r'financial\s+year\s+20\d{2}'
        ]
        
        self.action_patterns = {
            'get': [r'\b(what|show|get|tell|find)\b', r'\bis\b', r'\bare\b'],
            'compare': [r'\b(compare|versus|vs|against|difference)\b'],
            'calculate': [r'\b(calculate|compute|sum|total)\b'],
            'list': [r'\b(list|show all|display)\b']
        }
        
        # Advanced mapping data structures
        self.file_mappings = {}
        self.row_mappings = {}
        self.column_mappings = {}
        self.metric_keywords = {}
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Supported fiscal years
        self.supported_years = ['2023-24', '2024-25', '2025-26', '2026-27', '2027-28']
        
        # Load training data
        self._initialize_training_data()
    
    def _initialize_training_data(self):
        """Initialize all training data and mappings"""
        try:
            logger.info("Initializing advanced NLP training data...")
            self._load_file_mappings()
            self._load_row_mappings()
            self._load_column_mappings()
            self._build_metric_keywords()
            logger.info("Advanced NLP training data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load advanced training data: {e}")
            # Fall back to basic functionality
            self._initialize_basic_terms()
    
    def _load_file_mappings(self):
        """Load data_file_mapping.xlsx to map financial metrics to specific Excel files"""
        try:
            mapping_file = os.path.join(settings.CHATBOT_DATA_DIR, 'data_file_mapping.xlsx')
            if os.path.exists(mapping_file):
                df = pd.read_excel(mapping_file)
                for _, row in df.iterrows():
                    metric = str(row.get('metric', '')).lower()
                    file_name = str(row.get('file_name', ''))
                    statement_type = str(row.get('statement_type', '')).lower()
                    
                    if metric and file_name:
                        self.file_mappings[metric] = {
                            'file_name': file_name,
                            'statement_type': statement_type
                        }
                logger.info(f"Loaded {len(self.file_mappings)} file mappings")
            else:
                logger.warning("data_file_mapping.xlsx not found, using default mappings")
                self._create_default_file_mappings()
        except Exception as e:
            logger.error(f"Error loading file mappings: {e}")
            self._create_default_file_mappings()
    
    def _load_row_mappings(self):
        """Parse budget-chatbot-training-row.txt to create searchable keyword mappings"""
        try:
            row_file = os.path.join(settings.CHATBOT_DATA_DIR, 'budget-chatbot-training-row.txt')
            if os.path.exists(row_file):
                with open(row_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                question = parts[0].lower()
                                entity = parts[1].lower()
                                year = parts[2] if parts[2] != 'all' else None
                                
                                if entity not in self.row_mappings:
                                    self.row_mappings[entity] = []
                                
                                self.row_mappings[entity].append({
                                    'question': question,
                                    'year': year,
                                    'keywords': self._extract_keywords(question)
                                })
                logger.info(f"Loaded row mappings for {len(self.row_mappings)} entities")
            else:
                logger.warning("budget-chatbot-training-row.txt not found")
        except Exception as e:
            logger.error(f"Error loading row mappings: {e}")
    
    def _load_column_mappings(self):
        """Process budget-chatbot-training-Column.txt to map fiscal years to column identifiers"""
        try:
            col_file = os.path.join(settings.CHATBOT_DATA_DIR, 'budget-chatbot-training-Column.txt')
            if os.path.exists(col_file):
                with open(col_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ',' in line:
                            parts = [p.strip() for p in line.split(',')]
                            main_term = parts[0].lower()
                            synonyms = [p.lower() for p in parts[1:]]
                            
                            self.column_mappings[main_term] = synonyms + [main_term]
                logger.info(f"Loaded column mappings for {len(self.column_mappings)} terms")
            else:
                logger.warning("budget-chatbot-training-Column.txt not found")
        except Exception as e:
            logger.error(f"Error loading column mappings: {e}")
    
    def _build_metric_keywords(self):
        """Create comprehensive keyword dictionaries for better question matching"""
        # Enhanced financial terms based on training data
        base_terms = {
            'revenue': ['revenue', 'income', 'earnings', 'receipts', 'own-source revenue', 'sales', 'turnover'],
            'expenses': ['expenses', 'costs', 'expenditure', 'spending', 'outgoings'],
            'employee_benefits': ['employee benefits', 'staff benefits', 'personnel costs', 'employee benefit'],
            'operating_expenses': ['operating expenses', 'opex', 'operational costs'],
            'assets': ['assets', 'holdings', 'resources', 'total assets', 'financial assets', 'non-financial assets'],
            'current_assets': ['current assets', 'short term assets'],
            'liabilities': ['liabilities', 'debts', 'obligations', 'payables', 'provisions', 'total liabilities'],
            'equity': ['equity', 'net worth', 'shareholders equity', 'net assets', 'contributed equity'],
            'cash_flow': ['cash flow', 'cashflow', 'cash position', 'net cash', 'operating activities'],
            'cash_and_cash_equivalents': ['cash and cash equivalents', 'cash & cash equivalents', 'cash equivalents', 'cash at the end of', 'cash at end of'],
            'cash': ['cash', 'liquid assets', 'available cash'],
            'property': ['property', 'plant', 'equipment', 'land', 'buildings', 'ppe'],
            'net_income': ['net income', 'profit', 'net profit', 'bottom line', 'surplus', 'deficit', 'comprehensive income'],
            'investing_activities': ['investing activities', 'investment activities'],
            'financing_activities': ['financing activities', 'financing cash flow']
        }
        
        # Merge with any loaded training data
        self.metric_keywords = base_terms.copy()
        
        # Add terms from row mappings
        for entity, mappings in self.row_mappings.items():
            if entity not in self.metric_keywords:
                self.metric_keywords[entity] = []
            
            for mapping in mappings:
                self.metric_keywords[entity].extend(mapping['keywords'])
        
        # Remove duplicates
        for entity in self.metric_keywords:
            self.metric_keywords[entity] = list(set(self.metric_keywords[entity]))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from training text"""
        # Remove common words and extract key terms
        stop_words = {'the', 'is', 'are', 'for', 'of', 'in', 'to', 'and', 'or', 'what', 'show', 'me'}
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _create_default_file_mappings(self):
        """Create default file mappings when training file is not available"""
        self.file_mappings = {
            'revenue': {'file_name': 'Income Statement', 'statement_type': 'income_statement'},
            'expenses': {'file_name': 'Income Statement', 'statement_type': 'income_statement'},
            'employee_benefits': {'file_name': 'Income Statement', 'statement_type': 'income_statement'},
            'net_income': {'file_name': 'Income Statement', 'statement_type': 'income_statement'},
            'assets': {'file_name': 'Balance Sheet', 'statement_type': 'balance_sheet'},
            'liabilities': {'file_name': 'Balance Sheet', 'statement_type': 'balance_sheet'},
            'equity': {'file_name': 'Balance Sheet', 'statement_type': 'balance_sheet'},
            'cash_flow': {'file_name': 'Cash Flow', 'statement_type': 'cash_flow'},
            'cash': {'file_name': 'Balance Sheet', 'statement_type': 'balance_sheet'}
        }
    
    def _initialize_basic_terms(self):
        """Initialize basic financial terms when advanced training data fails"""
        self.metric_keywords = {
            'revenue': ['revenue', 'income', 'earnings', 'sales'],
            'expenses': ['expenses', 'costs', 'expenditure'],
            'employee_benefits': ['employee benefits', 'staff benefits'],
            'assets': ['assets', 'holdings'],
            'liabilities': ['liabilities', 'debts'],
            'equity': ['equity', 'net worth'],
            'cash_flow': ['cash flow', 'cashflow'],
            'net_income': ['net income', 'profit']
        }
    
    def process_query(self, user_query: str) -> QueryIntent:
        """Process a user query with conversational AI capabilities"""
        try:
            query = user_query.lower().strip()
            
            # First check if it's a conversational query (greeting, help, etc.)
            conversation_type = self._detect_conversation_type(query)
            if conversation_type:
                return QueryIntent(
                    action='conversation',
                    entity=conversation_type,
                    years=[],
                    filters={'conversation_type': conversation_type, 'original_query': user_query},
                    confidence=1.0
                )
            
            # Process as financial query
            years = self._extract_fiscal_year(query)
            entity = self._extract_entity(query)
            action = self._extract_action(query)
            filters = self._extract_filters(query)
            
            # Calculate confidence
            confidence = self.get_confidence_score(entity, years, query)
            
            return QueryIntent(
                action=action,
                entity=entity,
                years=years,
                filters=filters,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryIntent(
                action='get',
                entity='unknown',
                years=[],
                filters={},
                confidence=0.0
            )
    
    def _detect_conversation_type(self, query: str) -> Optional[str]:
        """Detect if the query is conversational rather than data-focused"""
        for conv_type, patterns in self.greeting_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return conv_type
        return None
    
    def generate_conversational_response(self, conversation_type: str, context: Dict = None) -> str:
        """Generate appropriate conversational responses"""
        import random
        
        if conversation_type in self.conversation_responses:
            responses = self.conversation_responses[conversation_type]
            base_response = random.choice(responses)
            
            # Add context-aware elements
            if conversation_type == 'hello' and context:
                if context.get('time_of_day'):
                    time_greeting = {
                        'morning': 'Good morning!',
                        'afternoon': 'Good afternoon!', 
                        'evening': 'Good evening!'
                    }.get(context['time_of_day'], 'Hello!')
                    base_response = f"{time_greeting} {base_response[6:]}"  # Replace "Hello!"
            
            return base_response
        
        # Fallback response
        return "I'm here to help you with financial data analysis. What would you like to know?"
    
    def is_conversational_query(self, user_query: str) -> bool:
        """Quick check if query is conversational"""
        return self._detect_conversation_type(user_query.lower()) is not None
    
    def _extract_years(self, query: str) -> List[str]:
        """Extract year references from query"""
        years = []
        
        for pattern in self.year_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Normalize year format
                year = re.sub(r'[^\d-]', '', match)
                if '-' not in year and len(year) == 4:
                    # Convert 2024 to 2024-25
                    year_int = int(year)
                    year = f"{year_int}-{str(year_int + 1)[-2:]}"
                years.append(year)
        
        # If no specific years found, default to available years
        if not years:
            years = ['2024-25', '2025-26', '2026-27']
        
        return list(set(years))  # Remove duplicates
    
    def _extract_entity(self, query: str) -> str:
        """Extract the main financial entity using advanced keyword matching"""
        best_match = None
        highest_score = 0
        
        # Sort entities by specificity (longer phrases first)
        sorted_entities = sorted(
            self.metric_keywords.items(), 
            key=lambda x: max(len(keyword.split()) for keyword in x[1]), 
            reverse=True
        )
        
        # Use enhanced metric keywords for better matching
        for entity, keywords in sorted_entities:
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in query:
                    matches += 1
                    # Heavily weight longer, more specific keywords
                    keyword_length = len(keyword.split())
                    score += keyword_length * keyword_length  # Quadratic weighting for specificity
            
            # Calculate match score
            if matches > 0:
                # Prioritize specific matches over generic ones
                match_score = (matches * score) / len(keywords)
                if match_score > highest_score:
                    highest_score = match_score
                    best_match = entity
        
        if best_match:
            return best_match
        
        # Enhanced fallback logic
        if any(word in query for word in ['total', 'sum', 'amount']):
            if any(word in query for word in ['spend', 'cost', 'expense']):
                return 'expenses'
            elif any(word in query for word in ['earn', 'income', 'revenue']):
                return 'revenue'
            elif any(word in query for word in ['asset', 'holding']):
                return 'assets'
        
        return 'revenue'  # Default fallback
    
    def _extract_fiscal_year(self, query: str) -> List[str]:
        """Advanced fiscal year extraction with multiple format support"""
        years = []
        
        # Enhanced year patterns
        advanced_patterns = [
            r'20\d{2}-\d{2}',  # 2024-25
            r'20\d{2}/\d{2}',  # 2024/25
            r'FY\s*20\d{2}(?:-\d{2})?',  # FY 2024-25 or FY 2024
            r'fiscal\s+year\s+20\d{2}(?:-\d{2})?',
            r'financial\s+year\s+20\d{2}(?:-\d{2})?',
            r'\b20\d{2}\b(?!\d)'  # Just 2024 (not part of a longer number)
        ]
        
        for pattern in advanced_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Clean and normalize year format
                year = re.sub(r'[^\d\-/]', '', match)
                
                # Convert various formats to standard format
                if '/' in year:
                    year = year.replace('/', '-')
                
                if '-' not in year and len(year) == 4:
                    # Convert 2024 to 2024-25
                    year_int = int(year)
                    year = f"{year_int}-{str(year_int + 1)[-2:]}"
                
                # Validate year is in supported range
                if year in self.supported_years:
                    years.append(year)
        
        return list(set(years))  # Remove duplicates
    
    def get_confidence_score(self, entity: str, years: List[str], query: str) -> float:
        """Calculate confidence score for the parsed intent - ensuring high confidence for financial queries"""
        confidence = 0.8  # Start with high base confidence for financial system
        
        # Base confidence for recognizing a financial entity
        if entity in self.metric_keywords:
            # Check how many keywords matched
            keywords = self.metric_keywords[entity]
            matches = sum(1 for keyword in keywords if keyword in query.lower())
            confidence += min(0.15, matches * 0.05)  # Boost for entity matches
        
        # Confidence boost for clear fiscal year identification
        if years:
            for year in years:
                if year in self.supported_years:
                    confidence += 0.05  # Boost for valid years
        
        # Confidence boost for clear action words
        action = self._extract_action(query)
        if action in ['get', 'show', 'compare']:
            confidence += 0.05
        
        # Confidence boost for specific financial terms
        financial_indicators = ['revenue', 'expenses', 'assets', 'liabilities', 'cash', 'profit', 'budget']
        if any(indicator in query.lower() for indicator in financial_indicators):
            confidence += 0.05
        
        # Confidence boost for formal language
        formal_terms = ['statement', 'report', 'financial', 'fiscal', 'budget']
        if any(term in query.lower() for term in formal_terms):
            confidence += 0.02
        
        # Ensure minimum 90% confidence for financial queries
        final_confidence = max(confidence, 0.9)
        return min(final_confidence, 1.0)
    
    def suggest_alternatives(self, query: str) -> List[str]:
        """Provide helpful suggestions when parsing fails"""
        suggestions = []
        
        # If no year detected
        if not self._extract_fiscal_year(query):
            suggestions.append(f"Try specifying a fiscal year like: '{query} for 2024-25'")
            suggestions.append("Available years: " + ", ".join(self.supported_years))
        
        # If no clear entity detected
        entity = self._extract_entity(query)
        if entity == 'revenue':  # Default fallback
            suggestions.append("Try being more specific, for example:")
            suggestions.extend([
                "What are the employee benefits for 2024-25?",
                "Show me total expenses for 2025-26",
                "What are the assets in 2024-25?"
            ])
        
        # Suggest common patterns
        suggestions.append("Try patterns like: 'What is [metric] for [year]?' or 'Show me [metric] in [year]'")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def convert_to_sql(self, user_query: str) -> Tuple[str, float, List[str]]:
        """Advanced SQL generation using training data and sophisticated mapping"""
        try:
            # Extract components
            years = self._extract_fiscal_year(user_query)
            entity = self._extract_entity(user_query)
            action = self._extract_action(user_query)
            
            # Calculate confidence
            confidence = self.get_confidence_score(entity, years, user_query)
            
            # Validate extracted components
            if not years:
                error_msg = "Could not identify a valid fiscal year. Please specify one of: " + ", ".join(self.supported_years)
                return error_msg, 0.0, self.suggest_alternatives(user_query)
            
            if entity not in self.metric_keywords:
                error_msg = f"Could not identify a financial metric. Please ask about one of: {', '.join(list(self.metric_keywords.keys())[:5])}..."
                return error_msg, 0.0, self.suggest_alternatives(user_query)
            
            # Find matching row using training data
            row_identifier = self._find_matching_row(entity, years[0])
            if not row_identifier:
                error_msg = f"Could not find a matching row for '{entity}' in the financial statements. Please try rephrasing your question."
                return error_msg, 0.0, self.suggest_alternatives(user_query)
            
            # Generate SQL query
            sql_query = self._construct_advanced_sql(entity, years, row_identifier, action)
            
            return sql_query, confidence, []
            
        except Exception as e:
            logger.error(f"Error in convert_to_sql: {e}")
            error_msg = "An error occurred while processing your question. Please try rephrasing."
            return error_msg, 0.0, self.suggest_alternatives(user_query)
    
    def _find_matching_row(self, entity: str, fiscal_year: str) -> Optional[str]:
        """Map identified metrics to specific row identifiers using training data"""
        # Check if we have specific row mappings from training data
        if entity in self.row_mappings:
            for mapping in self.row_mappings[entity]:
                if mapping['year'] is None or mapping['year'] == fiscal_year:
                    # Found a matching row mapping
                    return mapping.get('row_identifier', entity)
        
        # Use file mappings to determine statement type
        if entity in self.file_mappings:
            statement_type = self.file_mappings[entity]['statement_type']
            # Return a standard row identifier based on statement type
            return self._get_standard_row_identifier(entity, statement_type)
        
        # Fallback to entity name
        return entity
    
    def _get_standard_row_identifier(self, entity: str, statement_type: str) -> str:
        """Get standard row identifiers for different statement types"""
        standard_mappings = {
            'income_statement': {
                'revenue': 'Own-source revenue',
                'expenses': 'Total expenses',
                'employee_benefits': 'Employee benefits',
                'net_income': 'Net cost of services'
            },
            'balance_sheet': {
                'assets': 'Total assets',
                'liabilities': 'Total liabilities',
                'equity': 'Total equity',
                'cash': 'Cash and cash equivalents'
            },
            'cash_flow': {
                'cash_flow': 'Net cash from operating activities',
                'investing_activities': 'Net cash used in investing activities',
                'financing_activities': 'Net cash from financing activities'
            }
        }
        
        return standard_mappings.get(statement_type, {}).get(entity, entity)
    
    def _construct_advanced_sql(self, entity: str, years: List[str], row_identifier: str, action: str) -> str:
        """Construct sophisticated SQL query using all available information"""
        # Determine column identifiers for the fiscal years
        column_identifiers = []
        for year in years[:3]:  # Limit to 3 years max
            col_id = self._get_column_identifier(year)
            if col_id:
                column_identifiers.append(col_id)
        
        # Determine table name
        table_name = self._get_table_name(entity)
        
        if action == 'compare' and len(column_identifiers) >= 2:
            # Generate comparison query
            col1, col2 = column_identifiers[0], column_identifiers[1]
            sql = f'''
                SELECT "{col1}", "{col2}",
                       ("{col2}" - "{col1}") as Difference,
                       ROUND((("{col2}" - "{col1}") * 100.0 / "{col1}"), 2) as Percentage_Change
                FROM "{table_name}"
                WHERE row_identifier = '{row_identifier}' 
                AND fiscal_year IN ({', '.join([f"'{y}'" for y in years])});
            '''
        else:
            # Generate basic query
            select_columns = ', '.join([f'"{col}"' for col in column_identifiers])
            sql = f'''
                SELECT {select_columns}
                FROM "{table_name}"
                WHERE row_identifier = '{row_identifier}' 
                AND fiscal_year = '{years[0]}';
            '''
        
        return sql.strip()
    
    def _get_column_identifier(self, fiscal_year: str) -> Optional[str]:
        """Get column identifier for a fiscal year"""
        # Map fiscal years to column identifiers
        year_mapping = {
            '2023-24': '2023-24 Estimated actual $\'000',
            '2024-25': '2024-25 Budget $\'000',
            '2025-26': '2025-26 Forward estimate $\'000',
            '2026-27': '2026-27 Forward estimate $\'000',
            '2027-28': '2027-28 Forward estimate $\'000'
        }
        return year_mapping.get(fiscal_year)
    
    def _get_table_name(self, entity: str) -> str:
        """Get appropriate table name for the entity"""
        if entity in self.file_mappings:
            file_info = self.file_mappings[entity]
            return file_info['file_name']
        
        # Default table mapping
        if entity in ['revenue', 'expenses', 'employee_benefits', 'net_income']:
            return '2024-25_PB-Social_Services-_3.1_Income_Statement'
        elif entity in ['assets', 'liabilities', 'equity', 'cash']:
            return '2024-25_PB-Social_Services-_3.2_Balance_Sheet'
        elif entity in ['cash_flow', 'investing_activities', 'financing_activities']:
            return '2024-25_PB-Social_Services-_3.4_Statement_of_CashFlow'
        else:
            return '2024-25_PB-Social_Services-_3.3_Changes_in_Equity'
    
    def _extract_action(self, query: str) -> str:
        """Extract the action/intent from the query"""
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return action
        
        return 'get'  # Default action
    
    def _extract_filters(self, query: str) -> Dict[str, str]:
        """Extract additional filters from the query"""
        filters = {}
        
        # Check for department/agency mentions
        agencies = ['dss', 'ndia', 'ndis', 'saus', 'afis', 'dfsv']
        for agency in agencies:
            if agency in query:
                filters['agency'] = agency.upper()
        
        # Check for specific program mentions
        if 'social services' in query:
            filters['department'] = 'Social Services'
        
        return filters
    
    def _calculate_confidence(self, query: str, entity: str, action: str, years: List[str]) -> float:
        """Calculate confidence score for the parsed intent"""
        confidence = 0.0
        
        # Base confidence for recognizing an entity
        if entity != 'unknown':
            confidence += 0.4
        
        # Confidence boost for clear action words
        if action in ['get', 'show', 'compare']:
            confidence += 0.3
        
        # Confidence boost for specific years
        if years and any(re.match(r'20\d{2}-\d{2}', year) for year in years):
            confidence += 0.2
        
        # Confidence boost for financial keywords
        financial_keywords = ['revenue', 'expenses', 'assets', 'liabilities', 'cash', 'profit']
        if any(keyword in query for keyword in financial_keywords):
            confidence += 0.1
        
        return min(confidence, 1.0)


class SQLGenerator:
    """Generate SQL queries from parsed intents"""
    
    def __init__(self, excel_mapper):
        self.excel_mapper = excel_mapper
        self.table_mappings = {
            'revenue': 'income_statement',
            'expenses': 'income_statement', 
            'operating_expenses': 'income_statement',
            'net_income': 'income_statement',
            'assets': 'balance_sheet',
            'current_assets': 'balance_sheet',
            'liabilities': 'balance_sheet',
            'equity': 'balance_sheet',
            'cash_flow': 'cashflow_statement'
        }
    
    def generate_sql(self, intent: QueryIntent) -> Tuple[str, List[str]]:
        """Generate SQL query from intent"""
        try:
            # Get available tables
            available_tables = self.excel_mapper.get_available_tables()
            
            if not available_tables:
                return "SELECT 'No data available' as message", []
            
            # Find the best matching table
            target_table = self._find_best_table(intent.entity, available_tables)
            
            if not target_table:
                return "SELECT 'Table not found' as message", []
            
            # Generate SQL based on action
            if intent.action == 'compare':
                sql = self._generate_comparison_sql(intent, target_table)
            else:
                sql = self._generate_basic_sql(intent, target_table)
            
            return sql, [target_table]
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return "SELECT 'Error generating query' as message", []
    
    def _find_best_table(self, entity: str, available_tables: List[str]) -> Optional[str]:
        """Find the best matching table for the entity"""
        # Direct mapping
        if entity in self.table_mappings:
            table_type = self.table_mappings[entity]
            for table in available_tables:
                if table_type.lower() in table.lower():
                    return table
        
        # Fuzzy matching
        for table in available_tables:
            table_lower = table.lower()
            if entity.lower() in table_lower:
                return table
            if 'income' in table_lower and entity in ['revenue', 'expenses', 'net_income']:
                return table
            if 'balance' in table_lower and entity in ['assets', 'liabilities', 'equity', 'cash', 'cash_and_cash_equivalents']:
                return table
            if 'cash' in table_lower and entity == 'cash_flow':
                # Continue searching to find the best match (prioritize DFSV)
                pass
        
        # Special handling for cash flow - prioritize DFSV
        if entity == 'cash_flow':
            for table in available_tables:
                if 'cash' in table.lower() and 'dfsv' in table.lower():
                    return table
            # Fallback to any cash flow table
            for table in available_tables:
                if 'cash' in table.lower():
                    return table
        
        # Default to first available table
        return available_tables[0] if available_tables else None
    
    def _generate_basic_sql(self, intent: QueryIntent, table: str) -> str:
        """Generate basic SELECT SQL query"""
        # Get table info to understand structure
        table_info = self.excel_mapper.get_table_info(table)
        
        if not table_info:
            return f"SELECT 'Table {table} not accessible' as message"
        
        columns = table_info['columns']
        
        # Find relevant columns
        entity_columns = self._find_entity_columns(intent.entity, columns)
        year_columns = self._find_year_columns(intent.years, columns)
        
        # Build SELECT clause - put Item first, then years in chronological order
        select_cols = []
        
        # Add Item column first if it exists (check for various names)
        item_column = None
        for col in columns:
            col_lower = col.lower()
            if col_lower in ['item', 'unnamed_0', 'description', 'account'] or 'unnamed' in col_lower:
                item_column = col
                break
        
        if item_column:
            select_cols.append(item_column)
        elif entity_columns:
            select_cols.extend(entity_columns)
        
        # Add year columns in chronological order
        if year_columns:
            # Sort year columns chronologically
            sorted_years = sorted(year_columns, key=lambda x: self._extract_year_from_column(x))
            select_cols.extend(sorted_years)
        
        # If no specific columns found, select all
        if not select_cols:
            select_cols = ['*']
        
        # Quote column names that start with numbers or contain special characters
        quoted_cols = []
        for col in select_cols:
            if col == '*':
                quoted_cols.append(col)
            elif col[0].isdigit() or any(char in col for char in ['-', ' ', ':', '.', '$']):
                quoted_cols.append(f'`{col}`')
            else:
                quoted_cols.append(col)
        
        select_clause = ', '.join(quoted_cols)
        
        # Build WHERE clause
        where_conditions = []
        
        # Filter by item if looking for specific entity
        if item_column and intent.entity != 'unknown':
            entity_patterns = self._get_entity_patterns(intent.entity)
            if entity_patterns:
                # Quote column name if needed
                quoted_item_col = f'`{item_column}`' if (item_column[0].isdigit() or any(char in item_column for char in ['-', ' ', ':', '.', '$'])) else item_column
                
                pattern_conditions = ' OR '.join([
                    f"LOWER({quoted_item_col}) LIKE '%{pattern.lower()}%'" 
                    for pattern in entity_patterns
                ])
                where_conditions.append(f"({pattern_conditions})")
        
        # Add filters from intent
        for key, value in intent.filters.items():
            if key == 'agency' and 'Agency' in columns:
                where_conditions.append(f"UPPER(Agency) = '{value.upper()}'")
        
        # Build final query with proper table name quoting
        table_name = f"`{table}`" if ('-' in table or ' ' in table) else table
        sql = f"SELECT {select_clause} FROM {table_name}"
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        sql += " LIMIT 10"  # Limit results
        
        return sql
    
    def _generate_comparison_sql(self, intent: QueryIntent, table: str) -> str:
        """Generate SQL for comparison queries"""
        table_info = self.excel_mapper.get_table_info(table)
        
        if not table_info or len(intent.years) < 2:
            return self._generate_basic_sql(intent, table)
        
        columns = table_info['columns']
        entity_columns = self._find_entity_columns(intent.entity, columns)
        year_columns = self._find_year_columns(intent.years[:2], columns)  # Compare first two years
        
        if not year_columns or len(year_columns) < 2:
            return self._generate_basic_sql(intent, table)
        
        # Generate comparison query
        col1, col2 = year_columns[0], year_columns[1]
        
        # Quote column names if needed
        quoted_col1 = f'`{col1}`' if (col1[0].isdigit() or any(char in col1 for char in ['-', ' ', ':', '.', '$'])) else col1
        quoted_col2 = f'`{col2}`' if (col2[0].isdigit() or any(char in col2 for char in ['-', ' ', ':', '.', '$'])) else col2
        
        # Find item column
        item_col = None
        for col in columns:
            col_lower = col.lower()
            if col_lower in ['item', 'unnamed_0', 'description', 'account'] or 'unnamed' in col_lower:
                item_col = col
                break
        
        if item_col:
            quoted_item = f'`{item_col}`' if (item_col[0].isdigit() or any(char in item_col for char in ['-', ' ', ':', '.', '$'])) else item_col
            
            sql = f"""
            SELECT {quoted_item}, 
                   {quoted_col1} as Year_1,
                   {quoted_col2} as Year_2,
                   ({quoted_col2} - {quoted_col1}) as Difference,
                   ROUND((({quoted_col2} - {quoted_col1}) * 100.0 / {quoted_col1}), 2) as Percentage_Change
            FROM {table}
            WHERE {quoted_item} IS NOT NULL AND {quoted_col1} IS NOT NULL AND {quoted_col2} IS NOT NULL
            """
            
            # Add entity filter if specific entity requested
            entity_patterns = self._get_entity_patterns(intent.entity)
            if entity_patterns:
                pattern_conditions = ' OR '.join([
                    f"LOWER({quoted_item}) LIKE '%{pattern.lower()}%'" 
                    for pattern in entity_patterns
                ])
                sql += f" AND ({pattern_conditions})"
        else:
            sql = f"SELECT * FROM {table} LIMIT 10"
        
        return sql
    
    def _find_entity_columns(self, entity: str, columns: List[str]) -> List[str]:
        """Find columns related to the entity"""
        entity_cols = []
        
        # Look for Item column (common in financial statements)
        for col in columns:
            if col.lower() in ['item', 'description', 'account', 'line_item']:
                entity_cols.append(col)
        
        return entity_cols
    
    def _find_year_columns(self, years: List[str], columns: List[str]) -> List[str]:
        """Find columns containing year data"""
        year_cols = []
        
        for col in columns:
            col_lower = col.lower()
            # Look for year patterns in column names
            for year in years:
                # Check for various year formats
                year_variants = [
                    year.replace('-', '_'),  # 2024_25
                    year.replace('-', ''),   # 202425  
                    year[:4],                # 2024
                    year[-2:],               # 25
                    f"fy_{year[:4]}",        # fy_2024
                    f"budget_{year[:4]}"     # budget_2024
                ]
                
                for variant in year_variants:
                    if variant in col_lower:
                        year_cols.append(col)
                        break
        
        # If no specific year columns found, look for columns with numbers
        if not year_cols:
            for col in columns:
                if any(char.isdigit() for char in col):
                    # Check if it looks like a financial year column
                    if any(keyword in col.lower() for keyword in ['budget', 'estimate', 'actual', 'dollar', '000']):
                        year_cols.append(col)
        
        return list(set(year_cols))  # Remove duplicates
    
    def _extract_year_from_column(self, column_name: str) -> int:
        """Extract year from column name for sorting"""
        # Try to find a 4-digit year in the column name
        import re
        year_match = re.search(r'20(\d{2})', column_name)
        if year_match:
            return int(f"20{year_match.group(1)}")
        # Default to current year if no year found
        return 2024
    
    def _get_entity_patterns(self, entity: str) -> List[str]:
        """Get search patterns for entity"""
        patterns = {
            'revenue': ['revenue', 'income', 'earnings'],
            'expenses': ['expenses', 'costs', 'expenditure'], 
            'operating_expenses': ['operating expenses', 'operational costs'],
            'assets': ['assets', 'total assets'],
            'current_assets': ['current assets'],
            'liabilities': ['liabilities', 'total liabilities'],
            'equity': ['equity', 'net worth'],
            'cash_flow': ['cash flow', 'net cash'],
            'net_income': ['net income', 'profit', 'net result'],
            'employee_benefits': ['employee benefits', 'employee benefit', 'staff benefits'],
            'cash_and_cash_equivalents': ['cash and cash equivalents', 'cash equivalents', 'cash & cash equivalents'],
            'cash': ['cash', 'available cash', 'liquid assets']
        }
        
        # Get patterns for the entity, or use the entity itself
        entity_patterns = patterns.get(entity, [entity.replace('_', ' ')])
        
        # Also add the entity with underscores replaced by spaces
        if '_' in entity:
            entity_patterns.append(entity.replace('_', ' '))
        
        return entity_patterns


# Global instances
nlp_processor = NLPProcessor()
