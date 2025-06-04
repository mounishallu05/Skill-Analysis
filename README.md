# LinkedIn Skill Analysis Bot

A powerful tool that helps professionals identify skill gaps by comparing their LinkedIn profile skills against industry demands.

## 🎯 Features

- LinkedIn Profile Analysis
  - Extract skills from public profiles or uploaded PDFs
  - Parse experience and about sections
  - Skill endorsement analysis

- Job Market Analysis
  - Scrape job postings from major platforms
  - Extract and normalize required skills
  - Track skill trends over time

- Skill Gap Analysis
  - Compare personal skills against job requirements
  - Identify missing in-demand skills
  - Generate personalized skill development recommendations

- Interactive Dashboard
  - Visualize skill matches and gaps
  - Track skill trends
  - Generate detailed reports

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Chrome/Firefox (for web scraping)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd linkedin-skill-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLP models:
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt wordnet stopwords
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Usage

1. Start the application:
```bash
python src/main.py
```

2. Access the web interface at `http://localhost:8000`

3. Upload your LinkedIn profile PDF or provide your public profile URL

4. View your skill analysis and recommendations

## 📊 Project Structure

```
linkedin-skill-analysis/
├── src/
│   ├── scrapers/         # Web scraping modules
│   ├── processors/       # Data processing and analysis
│   ├── database/         # Database models and operations
│   ├── api/             # FastAPI endpoints
│   └── utils/           # Helper functions
├── tests/               # Unit and integration tests
├── config/             # Configuration files
├── data/               # Data storage
└── docs/              # Documentation
```

## ⚠️ Important Notes

- This tool is for educational and personal use only
- Respect LinkedIn's Terms of Service when scraping
- Use responsibly and ethically
- Consider rate limiting and data privacy

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 