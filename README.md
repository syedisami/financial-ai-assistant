# 🤖 Financial AI Assistant

A sophisticated Django-based chatbot that provides intelligent analysis of financial data through natural language queries. Built with advanced NLP processing, modern UI design, and comprehensive Excel data integration.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Django](https://img.shields.io/badge/django-v5.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎯 **Advanced NLP Processing**
- Natural language query understanding
- Intent recognition and entity extraction
- Fiscal year parsing (2024-25, FY 2024, etc.)
- 90%+ confidence scoring system
- Conversational AI with greetings and context

### 📊 **Financial Data Analysis**
- Excel file integration (Income Statement, Balance Sheet, Cash Flow)
- SQL query generation from natural language
- Multi-year comparisons and trend analysis
- Automatic data formatting and currency display
- Support for Australian Government budget data

### 🎨 **Modern UI/UX**
- Professional fintech-inspired design
- Responsive mobile-first layout
- Interactive suggestion chips
- Real-time confidence indicators
- Smooth animations and micro-interactions
- FAQ section with search functionality

### 🔧 **Technical Features**
- Django REST API architecture
- Pandas-based data processing
- Robust error handling and validation
- Static file management
- CSRF protection
- Comprehensive logging

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- Excel data files (Income Statement, Balance Sheet, Cash Flow, Training data)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/financial-ai-assistant.git
cd financial-ai-assistant
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django djangorestframework pandas openpyxl pandasql
```

### 4. Configure Data Directory
Update `chatbot_project/settings.py`:
```python
CHATBOT_DATA_DIR = Path(r'your/path/to/excel/files')
```

### 5. Set Up Database
```bash
python manage.py migrate
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/chatbot/` to access the application.

## 📁 Project Structure

```
financial-ai-assistant/
├── chatbot/                    # Main application
│   ├── management/
│   │   └── commands/          # Django management commands
│   ├── static/chatbot/        # Static assets
│   │   ├── css/style.css      # Modern UI styles
│   │   └── js/main.js         # Interactive functionality
│   ├── templates/chatbot/     # HTML templates
│   ├── excel_mapper.py        # Excel data processing
│   ├── nlp_processor.py       # Natural language processing
│   ├── utils.py               # Utility functions
│   └── views.py               # API and view logic
├── chatbot_project/           # Django project settings
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎮 Usage Examples

### Natural Language Queries
```
"What is the revenue for 2024-25?"
"Show me cash flow for the current year"
"Compare expenses between 2024-25 and 2025-26"
"What are the total assets?"
```

### Conversational Interface
```
User: "Hello"
Bot: "Good morning! I'm your financial data assistant. How may I help you today?"

User: "Show me revenue"
Bot: "Here are the revenue breakdown:
• Revenue from Government: $5.7 million
• Total comprehensive income: $0.00
Total: $5.7 million"
```

## 🔧 Configuration

### Data Files Required
Place these Excel files in your data directory:
- `2024-25_PB-Social_Services-_3.1_Income_Statement_*.xlsx`
- `2024-25_PB-Social_Services-_3.2_Balance_Sheet_*.xlsx`
- `2024-25_PB-Social_Services-_3.3_Cash_Flow_*.xlsx`
- `data_file_mapping.xlsx`
- `budget-chatbot-training-row.txt`
- `budget-chatbot-training-Column.txt`

### Environment Variables
Create a `.env` file for sensitive settings:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🧪 Testing

### Run Management Commands
```bash
# Test NLP processing
python manage.py test_advanced_nlp

# Test conversational features
python manage.py test_conversation

# Inspect data structure
python manage.py inspect_data
```

### API Testing
```bash
# Test API endpoint
curl -X POST http://127.0.0.1:8000/chatbot/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue for 2024-25?"}'
```

## 🎨 UI Features

### Design System
- **Color Palette**: Deep navy, vibrant accents, soft neutrals
- **Typography**: Clean sans-serif with distinct weights
- **Layout**: Card-based with rounded corners and shadows
- **Animations**: Subtle micro-interactions and transitions

### Components
- **Chat Interface**: Alternating message bubbles with avatars
- **Suggestion Chips**: Clickable quick-action buttons
- **Confidence Meter**: Visual trust score indicators
- **FAQ Accordion**: Searchable frequently asked questions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the robust web framework
- Pandas team for powerful data processing capabilities
- Font Awesome for beautiful icons
- Modern CSS techniques for responsive design

## 📞 Support

For support, questions, or feature requests:
- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/financial-ai-assistant/issues)
- 📖 Documentation: [Wiki](https://github.com/yourusername/financial-ai-assistant/wiki)

---

**Built with ❤️ using Django, Python, and modern web technologies.**