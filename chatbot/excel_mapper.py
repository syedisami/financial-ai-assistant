"""
Excel file mapping and SQL execution module.
This module handles Excel file operations, SQL query execution, and data retrieval.
"""

import pandas as pd
import os
import re
from pathlib import Path
from pandasql import sqldf
import openpyxl
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ExcelMapper:
    """Handle Excel file operations and SQL execution"""
    
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or settings.CHATBOT_DATA_DIR
        self.excel_files = {}
        self.dataframes = {}
        self.file_mappings = None
        self.loaded = False
    
    def load_excel_files(self):
        """Load all Excel files into memory"""
        try:
            if not os.path.exists(self.data_dir):
                logger.warning(f"Data directory does not exist: {self.data_dir}")
                return False
            
            # Expected Excel files
            file_patterns = [
                r".*Income Statement.*\.xlsx?$",
                r".*Balance Sheet.*\.xlsx?$", 
                r".*Changes in Equity.*\.xlsx?$",
                r".*Statement of CashFlow.*\.xlsx?$"
            ]
            
            files_found = []
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith(('.xlsx', '.xls')):
                        files_found.append(os.path.join(root, file))
            
            logger.info(f"Found {len(files_found)} Excel files in {self.data_dir}")
            
            for file_path in files_found:
                try:
                    filename = os.path.basename(file_path)
                    logger.info(f"Loading {filename}")
                    
                    # Read Excel file with multiple sheets
                    excel_file = pd.ExcelFile(file_path)
                    sheets_data = {}
                    
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                            # Clean column names - handle multiline and special characters
                            df.columns = df.columns.astype(str)
                            cleaned_columns = []
                            for col in df.columns:
                                # Remove newlines and excessive whitespace
                                clean_col = ' '.join(col.split())
                                # Replace special characters
                                clean_col = (clean_col.replace(' ', '_')
                                           .replace('-', '_')
                                           .replace('\n', '_')
                                           .replace('$', 'Dollar')
                                           .replace("'", '')
                                           .replace('"', '')
                                           .replace(',', '_')
                                           .replace('(', '_')
                                           .replace(')', '_')
                                           .replace(':', '_')
                                           .replace('.', '_')
                                           .replace('/', '_')
                                           .replace('\\', '_'))
                                # Remove multiple underscores
                                clean_col = re.sub(r'_+', '_', clean_col)
                                # Remove leading/trailing underscores
                                clean_col = clean_col.strip('_')
                                cleaned_columns.append(clean_col)
                            
                            df.columns = cleaned_columns
                            sheets_data[sheet_name] = df
                            
                            # Create table name for SQL queries
                            table_name = self._create_table_name(filename, sheet_name)
                            self.dataframes[table_name] = df
                            
                        except Exception as e:
                            logger.error(f"Error loading sheet {sheet_name} from {filename}: {e}")
                    
                    self.excel_files[filename] = sheets_data
                    
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
            
            self.loaded = True
            logger.info(f"Successfully loaded {len(self.excel_files)} Excel files with {len(self.dataframes)} tables")
            return True
            
        except Exception as e:
            logger.error(f"Error in load_excel_files: {e}")
            return False
    
    def _create_table_name(self, filename, sheet_name):
        """Create a clean table name for SQL queries"""
        # Remove file extension
        base_name = os.path.splitext(filename)[0]
        # Clean and combine
        clean_name = f"{base_name}_{sheet_name}"
        # Replace special characters
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', clean_name)
        # Remove multiple underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        return clean_name
    
    def execute_sql(self, sql_query):
        """Execute SQL query on loaded dataframes"""
        try:
            if not self.loaded:
                self.load_excel_files()
            
            if not self.dataframes:
                return None, "No data available. Please ensure Excel files are loaded."
            
            # For pandasql, we need to create a clean environment with valid Python variable names
            # Create a mapping of clean names to dataframes
            clean_env = {}
            table_name_mapping = {}
            
            for original_table_name, df in self.dataframes.items():
                # Create a valid Python variable name
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', original_table_name)
                clean_name = re.sub(r'_+', '_', clean_name)
                clean_name = clean_name.strip('_')
                
                # Ensure it doesn't start with a number
                if clean_name[0].isdigit():
                    clean_name = f"table_{clean_name}"
                
                clean_env[clean_name] = df
                table_name_mapping[original_table_name] = clean_name
            
            # Fix the SQL query to use clean table names
            fixed_query = sql_query
            for original_name, clean_name in table_name_mapping.items():
                # Replace table names in the query
                fixed_query = fixed_query.replace(f'FROM `{original_name}`', f'FROM {clean_name}')
                fixed_query = fixed_query.replace(f'FROM {original_name}', f'FROM {clean_name}')
                fixed_query = fixed_query.replace(f' `{original_name}` ', f' {clean_name} ')
                fixed_query = fixed_query.replace(f' {original_name} ', f' {clean_name} ')
            
            logger.info(f"Fixed SQL query: {fixed_query}")
            logger.info(f"Available tables in environment: {list(clean_env.keys())}")
            
            # Execute SQL query using pandasql
            result_df = sqldf(fixed_query, clean_env)
            
            if result_df is not None and not result_df.empty:
                return result_df, None
            else:
                return None, "Query returned no results."
                
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return None, f"SQL execution error: {str(e)}"
    
    def get_available_tables(self):
        """Get list of available tables for queries"""
        if not self.loaded:
            self.load_excel_files()
        return list(self.dataframes.keys())
    
    def get_table_info(self, table_name):
        """Get information about a specific table"""
        if table_name in self.dataframes:
            df = self.dataframes[table_name]
            return {
                'columns': list(df.columns),
                'rows': len(df),
                'sample_data': df.head(3).to_dict('records')
            }
        return None
    
    def search_columns(self, search_term):
        """Search for columns containing specific terms"""
        results = []
        search_term = search_term.lower()
        
        for table_name, df in self.dataframes.items():
            for col in df.columns:
                if search_term in col.lower():
                    results.append({
                        'table': table_name,
                        'column': col
                    })
        return results
    
    def format_financial_data(self, data):
        """Format financial data for display - keep original values for response text generation"""
        if data is None:
            return None
        
        try:
            # Convert DataFrame to list of dictionaries but keep original numeric values
            if hasattr(data, 'to_dict'):
                records = data.to_dict('records')
            else:
                records = data
            
            # Don't format currency values here - let the response formatter handle it
            # This preserves the original numeric values for calculations and text generation
            return records
            
        except Exception as e:
            logger.error(f"Error formatting data: {e}")
            return data


# Create sample data for testing if no Excel files exist
def create_sample_data():
    """Create sample financial data for testing"""
    return {
        'income_statement': pd.DataFrame({
            'Item': ['Revenue', 'Operating_Expenses', 'Net_Income'],
            'Year_2024_25': [1000000, 750000, 250000],
            'Year_2025_26': [1100000, 800000, 300000],
            'Year_2026_27': [1200000, 850000, 350000]
        }),
        'balance_sheet': pd.DataFrame({
            'Item': ['Current_Assets', 'Non_Current_Assets', 'Total_Assets', 'Current_Liabilities', 'Non_Current_Liabilities'],
            'Year_2024_25': [500000, 800000, 1300000, 200000, 300000],
            'Year_2025_26': [550000, 850000, 1400000, 220000, 320000],
            'Year_2026_27': [600000, 900000, 1500000, 240000, 340000]
        })
    }


# Global instance
excel_mapper = ExcelMapper()
