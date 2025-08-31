"""
Django management command to test conversational AI features.
"""

from django.core.management.base import BaseCommand
from chatbot.nlp_processor import nlp_processor


class Command(BaseCommand):
    help = 'Test conversational AI features'

    def handle(self, *args, **options):
        """Test conversational responses"""
        
        self.stdout.write("Testing Conversational AI Features...")
        self.stdout.write("=" * 40)
        
        # Test different conversational inputs
        test_conversations = [
            "Hi",
            "Hello",
            "Good morning",
            "Hey there",
            "Help",
            "What can you do?",
            "Thanks",
            "Goodbye",
            "Status",
            "What are the employee benefits for 2024-25?"  # Should be financial
        ]
        
        for i, conversation in enumerate(test_conversations, 1):
            self.stdout.write(f"\n{i}. Testing: '{conversation}'")
            self.stdout.write("-" * 30)
            
            try:
                # Test detection
                is_conversational = nlp_processor.is_conversational_query(conversation)
                self.stdout.write(f"Is conversational: {is_conversational}")
                
                # Test processing
                intent = nlp_processor.process_query(conversation)
                self.stdout.write(f"Action: {intent.action}")
                self.stdout.write(f"Entity: {intent.entity}")
                self.stdout.write(f"Confidence: {intent.confidence}")
                
                # Test response generation if conversational
                if intent.action == 'conversation':
                    response = nlp_processor.generate_conversational_response(
                        intent.entity, {'time_of_day': 'morning'}
                    )
                    self.stdout.write(f"Response: {response}")
                else:
                    self.stdout.write("Processing as financial query...")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS("Conversational testing complete!"))
