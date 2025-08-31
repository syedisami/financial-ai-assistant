from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import time
import logging

# Import our custom modules
from .excel_mapper import excel_mapper
from .nlp_processor import nlp_processor, SQLGenerator
from .utils import (
    validate_user_input, 
    handle_error, 
    suggestion_generator, 
    data_formatter,
    get_response_metadata
)
from .models import Log

logger = logging.getLogger(__name__)


def index(request):
    """Main chatbot interface"""
    return render(request, 'chatbot/index.html')


def chat(request):
    """Chat interface"""
    return render(request, 'chatbot/chat.html')


def faqs(request):
    """FAQ page"""
    return render(request, 'chatbot/faqs.html')


@api_view(['POST'])
def ask_question(request):
    """API endpoint to process chat questions"""
    start_time = time.time()
    
    try:
        data = request.data
        question = data.get('question', '').strip()
        
        # Validate input
        validation = validate_user_input(question)
        if not validation['valid']:
            return Response({
                'error': validation['error'],
                'status': 'error'
            }, status=400)
        
        question = validation['cleaned_input']
        
        # Load Excel data if not already loaded
        if not excel_mapper.loaded:
            excel_mapper.load_excel_files()
        
        # Check for context clues in follow-up questions
        context_entity = None
        original_question = question
        
        # Enhanced context detection for year-specific follow-ups
        if question.lower().strip() in ['give me the value', 'what is the value', 'show me the value', 'tell me the value']:
            # This is a follow-up question asking for a value
            # Try to infer context from recent successful queries
            # For now, we'll assume they're asking about cash and cash equivalents
            question = "What is the cash and cash equivalents for 2024-25?"
            logger.info(f"Context-enhanced question: {question}")
        elif any(year_pattern in question for year_pattern in ['2023-24', '2023/24', '2023-2024', '2022-23', '2025-26', '2024-2025', '2025-2026']) and len(question.split()) <= 3:
            # This looks like a year-only follow-up question like "2023-2024?"
            # Assume they want the same entity (cash) for a different year
            # Normalize the year format
            normalized_year = question.strip('?').strip()
            if '2023-2024' in normalized_year:
                normalized_year = '2023-24'
            elif '2024-2025' in normalized_year:
                normalized_year = '2024-25'
            elif '2025-2026' in normalized_year:
                normalized_year = '2025-26'
            
            question = f"What is the cash and cash equivalents for {normalized_year}?"
            logger.info(f"Year-based context enhancement: {original_question} -> {question}")
        
        # Process the question with NLP
        intent = nlp_processor.process_query(question)
        logger.info(f"Parsed intent: {intent}")
        
        # Handle conversational queries first
        if intent.action == 'conversation':
            conversation_type = intent.entity
            context = {'time_of_day': get_time_of_day()}
            
            response_text = nlp_processor.generate_conversational_response(
                conversation_type, context
            )
            
            # Generate helpful suggestions for conversational responses
            if conversation_type == 'hello':
                suggestions = [
                    "What are the employee benefits for 2024-25?",
                    "Show me revenue for 2025-26",
                    "Compare expenses between 2024-25 and 2025-26"
                ]
            elif conversation_type == 'help':
                suggestions = [
                    "What is the revenue for 2024-25?",
                    "Show me total assets",
                    "Compare cash flow across years"
                ]
            else:
                suggestions = ["What would you like to know about your financial data?"]
            
            execution_time = time.time() - start_time
            response_data = {
                'answer': response_text,
                'sql': None,
                'data': {'headers': [], 'rows': [], 'total_rows': 0},
                'suggestions': suggestions,
                'status': 'success',
                'metadata': get_response_metadata(question, execution_time, 0),
                'intent': {
                    'entity': intent.entity,
                    'action': intent.action,
                    'years': intent.years,
                    'confidence': intent.confidence,
                    'conversation_type': conversation_type
                }
            }
            
            # Log the conversation
            # Note: For conversational logs, we'll skip user field for now since this is API-only
            try:
                # Skip logging for now since we don't have user authentication in API
                pass
            except Exception as e:
                logger.warning(f"Could not log conversation: {e}")
            
            return Response(response_data)
        
        # Generate SQL query for financial data
        sql_generator = SQLGenerator(excel_mapper)
        sql_query, tables_used = sql_generator.generate_sql(intent)
        logger.info(f"Generated SQL: {sql_query}")
        
        # Execute SQL query
        result_data, error_msg = excel_mapper.execute_sql(sql_query)
        
        if error_msg:
            error_response = handle_error('sql_error', error_msg)
            return Response({
                'error': error_response['error'],
                'status': 'error',
                'sql': sql_query,
                'suggestions': suggestion_generator.get_popular_queries()[:3]
            }, status=500)
        
        # Format the results
        if result_data is not None and not result_data.empty:
            formatted_data = excel_mapper.format_financial_data(result_data)
            table_data = data_formatter.format_table_data(formatted_data)
            response_text = data_formatter.format_response_text(
                formatted_data, intent.entity, question
            )
            
            # Generate suggestions
            suggestions = suggestion_generator.generate_suggestions(
                question, formatted_data, intent.entity
            )
            
            # Prepare response
            execution_time = time.time() - start_time
            response_data = {
                'answer': response_text,
                'sql': sql_query,
                'data': table_data,
                'suggestions': suggestions,
                'status': 'success',
                'metadata': get_response_metadata(question, execution_time, len(formatted_data)),
                'intent': {
                    'entity': intent.entity,
                    'action': intent.action,
                    'years': intent.years,
                    'confidence': intent.confidence
                }
            }
            
            # Log the conversation (if user is authenticated)
            try:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    Log.objects.create(
                        user=request.user,
                        question=question,
                        sql=sql_query,
                        answer=response_text
                    )
            except Exception as log_error:
                logger.warning(f"Failed to log conversation: {log_error}")
            
            return Response(response_data)
        
        else:
            # No data found
            error_response = handle_error('data_not_found', 'No matching data found')
            return Response({
                'error': error_response['error'],
                'status': 'error',
                'sql': sql_query,
                'suggestions': suggestion_generator.get_popular_queries()[:3]
            }, status=404)
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        error_response = handle_error('processing_error', str(e))
        return Response({
            'error': error_response['error'],
            'status': 'error',
            'suggestions': suggestion_generator.get_popular_queries()[:3]
        }, status=500)


def get_time_of_day():
    """Get current time of day for contextual greetings"""
    from datetime import datetime
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return 'morning'
    elif 12 <= current_hour < 17:
        return 'afternoon'
    elif 17 <= current_hour < 22:
        return 'evening'
    else:
        return 'night'

@api_view(['GET'])
def health_check(request):
    """API health check endpoint"""
    try:
        # Load Excel data to get current status
        if not excel_mapper.loaded:
            excel_mapper.load_excel_files()
        
        available_tables = excel_mapper.get_available_tables()
        
        return Response({
            'status': 'healthy',
            'message': 'Financial chatbot API is running',
            'data_sources': {
                'available_tables': len(available_tables),
                'table_names': available_tables[:5],  # Show first 5 tables
                'total_excel_files': len(excel_mapper.excel_files),
                'data_loaded': excel_mapper.loaded
            },
            'features': {
                'nlp_processing': True,
                'sql_generation': True,
                'excel_data_access': len(available_tables) > 0,
                'response_formatting': True
            },
            'endpoints': [
                '/chatbot/api/ask/',
                '/chatbot/api/health/',
                '/chatbot/api/faqs/'
            ]
        })
    except Exception as e:
        return Response({
            'status': 'degraded',
            'message': f'API running but with issues: {str(e)}',
            'data_sources': {
                'available_tables': 0,
                'table_names': []
            }
        })


@api_view(['GET'])
def get_faqs(request):
    """Get FAQ data"""
    faqs = [
        {
            'question': 'How do I ask about a financial metric?',
            'answer': 'Simply ask in natural language, like "What is the revenue for 2024-25?" or "Show me operating expenses".'
        },
        {
            'question': 'What data is available?',
            'answer': 'The chatbot has access to financial statements including Income Statement, Balance Sheet, Changes in Equity, and Cash Flow statements.'
        },
        {
            'question': 'What years are covered?',
            'answer': 'Currently, data is available for fiscal years 2024-25, 2025-26, and 2026-27.'
        }
    ]
    
    return Response({
        'faqs': faqs,
        'total': len(faqs)
    })
