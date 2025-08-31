"""
Django management command to test specific queries and see actual data.
"""

from django.core.management.base import BaseCommand
from chatbot.excel_mapper import excel_mapper


class Command(BaseCommand):
    help = 'Test a specific query to see actual data'

    def handle(self, *args, **options):
        """Test query"""
        
        self.stdout.write("Loading Excel files...")
        excel_mapper.load_excel_files()
        
        # Test employee benefits query
        sql = "SELECT Unnamed_0, `2024_25_Budget_Dollar000` FROM table_2024_25_PB_Social_Services_3_1_Income_Statement_DFSV WHERE LOWER(Unnamed_0) LIKE '%employee benefits%' LIMIT 1"
        
        self.stdout.write(f"Executing SQL: {sql}")
        
        result, error = excel_mapper.execute_sql(sql)
        
        if error:
            self.stdout.write(self.style.ERROR(f"Error: {error}"))
        else:
            self.stdout.write(self.style.SUCCESS("Query successful!"))
            if result is not None:
                self.stdout.write(f"Result shape: {result.shape}")
                self.stdout.write(f"Columns: {list(result.columns)}")
                self.stdout.write("Data:")
                for index, row in result.iterrows():
                    self.stdout.write(f"  Row {index}: {dict(row)}")
                
                # Test formatting
                data_list = result.to_dict('records')
                self.stdout.write(f"As dict: {data_list}")
                
                from chatbot.utils import data_formatter
                formatted = data_formatter.format_response_text(data_list, "employee_benefits", "test query")
                self.stdout.write(f"Formatted response: {formatted}")
        
        # Also test a revenue query
        self.stdout.write("\n" + "="*50)
        self.stdout.write("Testing revenue query...")
        
        sql2 = "SELECT Unnamed_0, `2024_25_Budget_Dollar000` FROM table_2024_25_PB_Social_Services_3_1_Income_Statement_DFSV WHERE LOWER(Unnamed_0) LIKE '%revenue%' LIMIT 2"
        result2, error2 = excel_mapper.execute_sql(sql2)
        
        if error2:
            self.stdout.write(self.style.ERROR(f"Error: {error2}"))
        else:
            self.stdout.write("Revenue data:")
            for index, row in result2.iterrows():
                self.stdout.write(f"  {dict(row)}")
