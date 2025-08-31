"""
Create sample financial data for testing the chatbot functionality.
This module generates realistic sample data in the expected format.
"""

import pandas as pd
import os
from pathlib import Path
from django.conf import settings


def create_sample_excel_files():
    """Create sample Excel files with financial data"""
    
    data_dir = settings.CHATBOT_DATA_DIR
    os.makedirs(data_dir, exist_ok=True)
    
    # Sample Income Statement Data
    income_data = {
        'Item': [
            'Revenue from Government',
            'Revenue from Services', 
            'Other Revenue',
            'Total Revenue',
            'Employee Benefits',
            'Operating Expenses',
            'Finance Costs',
            'Total Expenses',
            'Net Income'
        ],
        'Year_2024_25': [
            850000000,  # 850M
            150000000,  # 150M
            25000000,   # 25M
            1025000000, # 1.025B
            450000000,  # 450M
            320000000,  # 320M
            15000000,   # 15M
            785000000,  # 785M
            240000000   # 240M
        ],
        'Year_2025_26': [
            920000000,  # 920M
            165000000,  # 165M
            28000000,   # 28M
            1113000000, # 1.113B
            475000000,  # 475M
            340000000,  # 340M
            18000000,   # 18M
            833000000,  # 833M
            280000000   # 280M
        ],
        'Year_2026_27': [
            980000000,  # 980M
            180000000,  # 180M
            32000000,   # 32M
            1192000000, # 1.192B
            500000000,  # 500M
            365000000,  # 365M
            20000000,   # 20M
            885000000,  # 885M
            307000000   # 307M
        ]
    }
    
    # Sample Balance Sheet Data
    balance_data = {
        'Item': [
            'Cash and Cash Equivalents',
            'Receivables',
            'Other Current Assets',
            'Total Current Assets',
            'Property Plant Equipment',
            'Intangible Assets',
            'Total Non-Current Assets',
            'Total Assets',
            'Accounts Payable',
            'Other Current Liabilities',
            'Total Current Liabilities',
            'Long-term Debt',
            'Other Non-Current Liabilities',
            'Total Non-Current Liabilities',
            'Total Liabilities',
            'Retained Earnings',
            'Other Equity',
            'Total Equity'
        ],
        'Year_2024_25': [
            120000000,  # Cash
            45000000,   # Receivables
            25000000,   # Other Current
            190000000,  # Total Current Assets
            850000000,  # PPE
            95000000,   # Intangibles
            945000000,  # Total Non-Current Assets
            1135000000, # Total Assets
            65000000,   # Payables
            45000000,   # Other Current Liab
            110000000,  # Total Current Liab
            200000000,  # Long-term Debt
            125000000,  # Other Non-Current Liab
            325000000,  # Total Non-Current Liab
            435000000,  # Total Liabilities
            520000000,  # Retained Earnings
            180000000,  # Other Equity
            700000000   # Total Equity
        ],
        'Year_2025_26': [
            135000000,  # Cash
            52000000,   # Receivables
            28000000,   # Other Current
            215000000,  # Total Current Assets
            890000000,  # PPE
            105000000,  # Intangibles
            995000000,  # Total Non-Current Assets
            1210000000, # Total Assets
            70000000,   # Payables
            50000000,   # Other Current Liab
            120000000,  # Total Current Liab
            220000000,  # Long-term Debt
            130000000,  # Other Non-Current Liab
            350000000,  # Total Non-Current Liab
            470000000,  # Total Liabilities
            580000000,  # Retained Earnings
            160000000,  # Other Equity
            740000000   # Total Equity
        ],
        'Year_2026_27': [
            155000000,  # Cash
            58000000,   # Receivables
            32000000,   # Other Current
            245000000,  # Total Current Assets
            925000000,  # PPE
            115000000,  # Intangibles
            1040000000, # Total Non-Current Assets
            1285000000, # Total Assets
            75000000,   # Payables
            55000000,   # Other Current Liab
            130000000,  # Total Current Liab
            240000000,  # Long-term Debt
            135000000,  # Other Non-Current Liab
            375000000,  # Total Non-Current Liab
            505000000,  # Total Liabilities
            650000000,  # Retained Earnings
            130000000,  # Other Equity
            780000000   # Total Equity
        ]
    }
    
    # Sample Cash Flow Data
    cashflow_data = {
        'Item': [
            'Net Income',
            'Depreciation and Amortization',
            'Changes in Working Capital',
            'Other Operating Activities',
            'Net Cash from Operating Activities',
            'Capital Expenditures',
            'Acquisitions',
            'Other Investing Activities',
            'Net Cash from Investing Activities',
            'Debt Issuance',
            'Debt Repayments',
            'Other Financing Activities',
            'Net Cash from Financing Activities',
            'Net Change in Cash',
            'Cash Beginning of Period',
            'Cash End of Period'
        ],
        'Year_2024_25': [
            240000000,  # Net Income
            85000000,   # Depreciation
            -15000000,  # Working Capital Change
            12000000,   # Other Operating
            322000000,  # Operating Cash Flow
            -95000000,  # CapEx
            -25000000,  # Acquisitions
            8000000,    # Other Investing
            -112000000, # Investing Cash Flow
            50000000,   # Debt Issuance
            -35000000,  # Debt Repayments
            -8000000,   # Other Financing
            7000000,    # Financing Cash Flow
            217000000,  # Net Change
            103000000,  # Beginning Cash
            120000000   # Ending Cash
        ],
        'Year_2025_26': [
            280000000,  # Net Income
            88000000,   # Depreciation
            -12000000,  # Working Capital Change
            15000000,   # Other Operating
            371000000,  # Operating Cash Flow
            -105000000, # CapEx
            -30000000,  # Acquisitions
            10000000,   # Other Investing
            -125000000, # Investing Cash Flow
            40000000,   # Debt Issuance
            -25000000,  # Debt Repayments
            -10000000,  # Other Financing
            5000000,    # Financing Cash Flow
            251000000,  # Net Change
            120000000,  # Beginning Cash
            135000000   # Ending Cash
        ],
        'Year_2026_27': [
            307000000,  # Net Income
            92000000,   # Depreciation
            -8000000,   # Working Capital Change
            18000000,   # Other Operating
            409000000,  # Operating Cash Flow
            -115000000, # CapEx
            -35000000,  # Acquisitions
            12000000,   # Other Investing
            -138000000, # Investing Cash Flow
            30000000,   # Debt Issuance
            -20000000,  # Debt Repayments
            -12000000,  # Other Financing
            -2000000,   # Financing Cash Flow
            269000000,  # Net Change
            135000000,  # Beginning Cash
            155000000   # Ending Cash
        ]
    }
    
    # Changes in Equity Data
    equity_data = {
        'Item': [
            'Beginning Equity',
            'Net Income',
            'Other Comprehensive Income',
            'Dividends Paid',
            'Share Issuance',
            'Other Equity Changes',
            'Ending Equity'
        ],
        'Year_2024_25': [
            460000000,  # Beginning
            240000000,  # Net Income
            15000000,   # Other Comprehensive
            -25000000,  # Dividends
            8000000,    # Share Issuance
            2000000,    # Other Changes
            700000000   # Ending
        ],
        'Year_2025_26': [
            700000000,  # Beginning
            280000000,  # Net Income
            18000000,   # Other Comprehensive
            -30000000,  # Dividends
            0,          # Share Issuance
            -228000000, # Other Changes (large adjustment)
            740000000   # Ending
        ],
        'Year_2026_27': [
            740000000,  # Beginning
            307000000,  # Net Income
            20000000,   # Other Comprehensive
            -35000000,  # Dividends
            0,          # Share Issuance
            -252000000, # Other Changes
            780000000   # Ending
        ]
    }
    
    # Create Excel files
    files_to_create = [
        ('2024-25 PB-Social Services- 3.1 Income Statement.xlsx', income_data),
        ('2024-25 PB-Social Services- 3.2 Balance Sheet.xlsx', balance_data),
        ('2024-25 PB-Social Services- 3.3 Changes in Equity.xlsx', equity_data),
        ('2024-25 PB-Social Services- 3.4 Statement of CashFlow.xlsx', cashflow_data)
    ]
    
    created_files = []
    
    for filename, data in files_to_create:
        try:
            df = pd.DataFrame(data)
            file_path = os.path.join(data_dir, filename)
            
            # Create Excel file with proper formatting
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            
            created_files.append(file_path)
            print(f"Created: {filename}")
            
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    return created_files


def create_sample_training_files():
    """Create sample training files for NLP"""
    
    data_dir = settings.CHATBOT_DATA_DIR
    
    # Sample training data - rows
    row_training = """
What is the revenue for 2024-25?|revenue|2024-25
Show me expenses for 2025-26|expenses|2025-26
What are total assets?|assets|all
Compare revenue across years|revenue|compare
What is net income for 2026-27?|net_income|2026-27
Show cash flow for 2024-25|cash_flow|2024-25
What are employee benefits?|employee_benefits|all
Compare expenses between 2024-25 and 2025-26|expenses|compare
Show me the balance sheet|balance_sheet|all
What is total equity for 2025-26?|equity|2025-26
"""
    
    # Sample training data - columns
    column_training = """
revenue,income,earnings,sales,turnover
expenses,costs,expenditure,spending,outgoings
assets,holdings,resources,property
liabilities,debts,obligations,payables
equity,net_worth,shareholders_equity
cash_flow,cashflow,cash_position
net_income,profit,net_profit,bottom_line
employee_benefits,staff_benefits,personnel_costs
operating_expenses,opex,operational_costs
current_assets,short_term_assets
"""
    
    # Create training files
    try:
        row_file_path = os.path.join(data_dir, 'budget-chatbot-training-row.txt')
        with open(row_file_path, 'w', encoding='utf-8') as f:
            f.write(row_training.strip())
        
        column_file_path = os.path.join(data_dir, 'budget-chatbot-training-Column.txt')
        with open(column_file_path, 'w', encoding='utf-8') as f:
            f.write(column_training.strip())
        
        # Data description file
        description = """
Financial Dataset Description:

This dataset contains Australian Government Social Services budget data covering:

1. Income Statement (3.1):
   - Revenue from Government appropriations
   - Revenue from services provided
   - Operating expenses including employee benefits
   - Net income/surplus

2. Balance Sheet (3.2):
   - Current and non-current assets
   - Cash and receivables
   - Property, plant and equipment
   - Current and non-current liabilities
   - Equity position

3. Changes in Equity (3.3):
   - Beginning and ending equity balances
   - Net income impact
   - Dividend payments and other equity changes

4. Cash Flow Statement (3.4):
   - Operating activities cash flow
   - Investing activities (capital expenditures)
   - Financing activities (debt and equity)
   - Net change in cash position

Time Period: 2024-25, 2025-26, 2026-27 financial years

Key Agencies: DSS, NDIA, NDIS, SAUS, AFIS, DFSV
"""
        
        desc_file_path = os.path.join(data_dir, 'data description.txt')
        with open(desc_file_path, 'w', encoding='utf-8') as f:
            f.write(description.strip())
        
        print("Created training and description files")
        return True
        
    except Exception as e:
        print(f"Error creating training files: {e}")
        return False


if __name__ == "__main__":
    # Create sample data if run directly
    created = create_sample_excel_files()
    create_sample_training_files()
    print(f"Sample data creation complete. Created {len(created)} files.")
