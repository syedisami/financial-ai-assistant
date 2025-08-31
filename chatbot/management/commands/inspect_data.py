"""
Django management command to inspect the actual Excel data structure.
"""

from django.core.management.base import BaseCommand
from chatbot.excel_mapper import excel_mapper


class Command(BaseCommand):
    help = 'Inspect the Excel data structure to understand column names and data'

    def handle(self, *args, **options):
        """Inspect Excel data"""
        
        self.stdout.write("Loading Excel files...")
        success = excel_mapper.load_excel_files()
        
        if not success:
            self.stdout.write(self.style.ERROR("Failed to load Excel files"))
            return
        
        tables = excel_mapper.get_available_tables()
        self.stdout.write(f"Found {len(tables)} tables:")
        
        for i, table in enumerate(tables[:5]):  # Show first 5 tables
            self.stdout.write(f"\n{i+1}. {table}")
            
            table_info = excel_mapper.get_table_info(table)
            if table_info:
                self.stdout.write(f"   Columns: {table_info['columns']}")
                self.stdout.write(f"   Rows: {table_info['rows']}")
                
                if table_info['sample_data']:
                    self.stdout.write("   Sample data:")
                    for j, row in enumerate(table_info['sample_data'][:2]):
                        self.stdout.write(f"     Row {j+1}: {row}")
        
        if len(tables) > 5:
            self.stdout.write(f"\n... and {len(tables) - 5} more tables")
        
        # Test a simple query
        self.stdout.write("\nTesting simple query...")
        try:
            first_table = tables[0] if tables else None
            if first_table:
                test_sql = f"SELECT * FROM `{first_table}` LIMIT 3"
                result, error = excel_mapper.execute_sql(test_sql)
                
                if error:
                    self.stdout.write(self.style.ERROR(f"Query failed: {error}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Query successful!"))
                    if result is not None:
                        self.stdout.write(f"Result shape: {result.shape}")
                        self.stdout.write(f"Columns: {list(result.columns)}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Test query error: {e}"))
