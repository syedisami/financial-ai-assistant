"""
Django management command to create sample training data files for the advanced NLP processor.
"""

import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create advanced training data files for NLP processor'

    def handle(self, *args, **options):
        """Create comprehensive training data files"""
        
        data_dir = settings.CHATBOT_DATA_DIR
        os.makedirs(data_dir, exist_ok=True)
        
        self.stdout.write("Creating advanced training data files...")
        
        # Create data file mapping
        self._create_file_mapping(data_dir)
        
        # Create row mapping training data
        self._create_row_mapping(data_dir)
        
        # Create column mapping training data
        self._create_column_mapping(data_dir)
        
        self.stdout.write(self.style.SUCCESS("Advanced training data files created successfully!"))
        self.stdout.write("\nFiles created:")
        self.stdout.write("- data_file_mapping.xlsx")
        self.stdout.write("- budget-chatbot-training-row.txt")
        self.stdout.write("- budget-chatbot-training-Column.txt")
        self.stdout.write("\nThe NLP processor now supports:")
        self.stdout.write("✓ Advanced entity recognition")
        self.stdout.write("✓ Confidence scoring")
        self.stdout.write("✓ Training data integration")
        self.stdout.write("✓ Sophisticated SQL generation")
        
    def _create_file_mapping(self, data_dir):
        """Create data_file_mapping.xlsx"""
        file_mappings = [
            {'metric': 'revenue', 'file_name': '2024-25_PB-Social_Services-_3.1_Income_Statement', 'statement_type': 'income_statement'},
            {'metric': 'income', 'file_name': '2024-25_PB-Social_Services-_3.1_Income_Statement', 'statement_type': 'income_statement'},
            {'metric': 'expenses', 'file_name': '2024-25_PB-Social_Services-_3.1_Income_Statement', 'statement_type': 'income_statement'},
            {'metric': 'employee_benefits', 'file_name': '2024-25_PB-Social_Services-_3.1_Income_Statement', 'statement_type': 'income_statement'},
            {'metric': 'net_income', 'file_name': '2024-25_PB-Social_Services-_3.1_Income_Statement', 'statement_type': 'income_statement'},
            {'metric': 'assets', 'file_name': '2024-25_PB-Social_Services-_3.2_Balance_Sheet', 'statement_type': 'balance_sheet'},
            {'metric': 'current_assets', 'file_name': '2024-25_PB-Social_Services-_3.2_Balance_Sheet', 'statement_type': 'balance_sheet'},
            {'metric': 'liabilities', 'file_name': '2024-25_PB-Social_Services-_3.2_Balance_Sheet', 'statement_type': 'balance_sheet'},
            {'metric': 'equity', 'file_name': '2024-25_PB-Social_Services-_3.2_Balance_Sheet', 'statement_type': 'balance_sheet'},
            {'metric': 'cash', 'file_name': '2024-25_PB-Social_Services-_3.2_Balance_Sheet', 'statement_type': 'balance_sheet'},
            {'metric': 'cash_flow', 'file_name': '2024-25_PB-Social_Services-_3.4_Statement_of_CashFlow', 'statement_type': 'cash_flow'},
            {'metric': 'investing_activities', 'file_name': '2024-25_PB-Social_Services-_3.4_Statement_of_CashFlow', 'statement_type': 'cash_flow'},
            {'metric': 'financing_activities', 'file_name': '2024-25_PB-Social_Services-_3.4_Statement_of_CashFlow', 'statement_type': 'cash_flow'},
            {'metric': 'opening_balance', 'file_name': '2024-25_PB-Social_Services-_3.3_Changes_in_Equity', 'statement_type': 'equity_changes'},
            {'metric': 'closing_balance', 'file_name': '2024-25_PB-Social_Services-_3.3_Changes_in_Equity', 'statement_type': 'equity_changes'},
        ]
        
        df = pd.DataFrame(file_mappings)
        df.to_excel(os.path.join(data_dir, 'data_file_mapping.xlsx'), index=False)
        self.stdout.write("✓ Created data_file_mapping.xlsx")
    
    def _create_row_mapping(self, data_dir):
        """Create budget-chatbot-training-row.txt"""
        row_mappings = [
            "what is the revenue for|revenue|2024-25|Revenue from Government",
            "show me total revenue|revenue|all|Revenue from Government",
            "what are the employee benefits|employee_benefits|all|Employee benefits",
            "total employee benefits for|employee_benefits|2024-25|Employee benefits",
            "show me staff benefits|employee_benefits|all|Employee benefits",
            "what are the total expenses|expenses|all|Total expenses",
            "total expenditure for|expenses|2024-25|Total expenses",
            "show me all costs|expenses|all|Total expenses",
            "what are the operating expenses|operating_expenses|all|Operating expenses",
            "total assets for|assets|all|Total assets",
            "what are the current assets|current_assets|all|Current assets",
            "show me financial assets|assets|all|Financial assets",
            "what are the total liabilities|liabilities|all|Total liabilities",
            "show me payables|liabilities|all|Payables",
            "what is the equity position|equity|all|Total equity",
            "total equity for|equity|2024-25|Total equity",
            "show me net assets|equity|all|Net assets",
            "what is the cash position|cash|all|Cash and cash equivalents",
            "total cash for|cash|2024-25|Cash and cash equivalents",
            "what is the cash flow|cash_flow|all|Net cash from operating activities",
            "operating cash flow for|cash_flow|2024-25|Net cash from operating activities",
            "what is the net income|net_income|all|Net cost of services",
            "total profit for|net_income|2024-25|Net cost of services",
            "show me comprehensive income|net_income|all|Total comprehensive income",
            "what are investing activities|investing_activities|all|Net cash used in investing activities",
            "financing activities for|financing_activities|2024-25|Net cash from financing activities",
            "opening balance for|opening_balance|all|Opening balance",
            "closing balance for|closing_balance|all|Closing balance",
        ]
        
        with open(os.path.join(data_dir, 'budget-chatbot-training-row.txt'), 'w', encoding='utf-8') as f:
            for mapping in row_mappings:
                f.write(mapping + '\\n')
        
        self.stdout.write("✓ Created budget-chatbot-training-row.txt")
    
    def _create_column_mapping(self, data_dir):
        """Create budget-chatbot-training-Column.txt"""
        column_mappings = [
            "2023-24, 2023/24, FY 2023-24, fiscal year 2023-24, estimated actual 2023-24",
            "2024-25, 2024/25, FY 2024-25, fiscal year 2024-25, budget 2024-25",
            "2025-26, 2025/26, FY 2025-26, fiscal year 2025-26, forward estimate 2025-26",
            "2026-27, 2026/27, FY 2026-27, fiscal year 2026-27, forward estimate 2026-27",
            "2027-28, 2027/28, FY 2027-28, fiscal year 2027-28, forward estimate 2027-28",
            "revenue, income, earnings, receipts, sales, turnover",
            "expenses, costs, expenditure, spending, outgoings",
            "assets, holdings, resources, property",
            "liabilities, debts, obligations, payables",
            "equity, net worth, net assets, shareholders equity",
            "cash, cash equivalents, liquid assets",
            "employee benefits, staff benefits, personnel costs, employee benefit",
            "operating expenses, opex, operational costs",
            "current assets, short term assets",
            "total assets, all assets",
            "total liabilities, all liabilities",
            "cash flow, cashflow, cash position",
            "net income, profit, net profit, surplus, deficit",
            "comprehensive income, total comprehensive income",
            "investing activities, investment activities",
            "financing activities, financing cash flow",
            "opening balance, beginning balance, start balance",
            "closing balance, ending balance, final balance",
        ]
        
        with open(os.path.join(data_dir, 'budget-chatbot-training-Column.txt'), 'w', encoding='utf-8') as f:
            for mapping in column_mappings:
                f.write(mapping + '\\n')
        
        self.stdout.write("✓ Created budget-chatbot-training-Column.txt")
