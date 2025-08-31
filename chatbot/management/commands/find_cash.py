"""
Django management command to find cash entries in the data.
"""

from django.core.management.base import BaseCommand
from chatbot.excel_mapper import excel_mapper


class Command(BaseCommand):
    help = 'Find cash entries in all tables'

    def handle(self, *args, **options):
        """Find cash entries"""
        
        self.stdout.write("Searching for cash entries...")
        
        # Load Excel data
        excel_mapper.load_excel_files()
        
        # Search for cash in all tables
        cash_found = False
        
        for table_name in excel_mapper.get_available_tables():
            if 'balance_sheet' in table_name.lower():
                self.stdout.write(f"\\nSearching in {table_name}...")
                
                try:
                    # Search for cash entries
                    sql = f"SELECT Unnamed_0, `2024_25_Budget_Dollar000` FROM `{table_name}` WHERE LOWER(Unnamed_0) LIKE '%cash%' LIMIT 10"
                    result, error = excel_mapper.execute_sql(sql)
                    
                    if error:
                        self.stdout.write(f"Error: {error}")
                        continue
                    
                    if result is not None and not result.empty:
                        cash_found = True
                        self.stdout.write(f"Found cash entries in {table_name}:")
                        for index, row in result.iterrows():
                            item = row.get('Unnamed_0', 'Unknown')
                            amount = row.get('2024_25_Budget_Dollar000', 'N/A')
                            self.stdout.write(f"  - {item}: {amount}")
                    else:
                        self.stdout.write("No cash entries found in this table")
                        
                except Exception as e:
                    self.stdout.write(f"Error querying {table_name}: {e}")
        
        if not cash_found:
            self.stdout.write("\\nNo cash entries found in any Balance Sheet tables")
            
            # Let's also check what's actually in the first balance sheet
            first_balance_sheet = None
            for table_name in excel_mapper.get_available_tables():
                if 'balance_sheet' in table_name.lower():
                    first_balance_sheet = table_name
                    break
                    
            if first_balance_sheet:
                self.stdout.write(f"\\nLet's see what's in {first_balance_sheet}:")
                try:
                    sql = f"SELECT Unnamed_0 FROM `{first_balance_sheet}` WHERE Unnamed_0 IS NOT NULL LIMIT 15"
                    result, error = excel_mapper.execute_sql(sql)
                    
                    if result is not None:
                        for index, row in result.iterrows():
                            item = row.get('Unnamed_0', 'Unknown')
                            self.stdout.write(f"  - {item}")
                except Exception as e:
                    self.stdout.write(f"Error: {e}")
        
        self.stdout.write("\\nSearch complete!")
