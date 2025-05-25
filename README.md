# Cognitive Warfare Data Analysis Dashboard

A comprehensive dashboard for analyzing cognitive warfare research data with advanced search, visualization, and comparison capabilities.

## Features

### 📍 Explore Tab
- Interactive sunburst visualization of cognitive warfare taxonomy (6 main categories, 74 elements)
- Click-through exploration from categories to individual text chunks
- Full filtering by sources, date ranges, and languages
- Download functionality for data export

### 🔍 Search Tab
- **3 Search Modes**: Keyword, Boolean, Semantic search
- Advanced query processing with progress indicators
- Search result visualization with category breakdown
- Export search results in multiple formats

### ⚖️ Compare Tab
- Side-by-side comparison of different data selections
- **4 Visualization Types**: Bar charts, Sunburst, Donut, Sankey diagrams
- Independent filter sets for detailed comparative analysis
- Statistical comparison summaries

### 📈 Burstiness Tab
- Temporal burst detection using statistical algorithms
- Configurable sensitivity and time granularity
- Interactive timeline visualizations with burst markers
- Category-specific burst analysis

### 📚 Sources Tab
- **5 Analysis Types**: Source Distribution, Language Analysis, Temporal Patterns, Taxonomy Coverage, Corpus Statistics
- Interactive charts and heatmaps
- Source comparison and metadata analysis

## Database Schema

The dashboard works with a PostgreSQL database containing:
- **Records**: Source documents from academic papers, parliamentary data, and research libraries
- **Chunks**: Text segments extracted from records
- **Classifications**: AI-powered taxonomy classifications with confidence scores

### Main Tables:
- `records` - Source documents with metadata
- `chunks` - Text chunks from documents  
- `chunk_classifications` - Taxonomy classifications (HLTP, 2nd_level_TE, 3rd_level_TE)

## Cognitive Warfare Taxonomy

### 6 Main Categories:
1. **Conceptual Foundations** - Definitional frameworks, theoretical traditions, doctrinal development
2. **Cognitive Target Domain** - Perceptual, emotional, cognitive, and social-cognitive processing
3. **Operational Scope** - Target scale, geographical scope, domain integration
4. **Counter-Measures** - Individual resilience, institutional defenses, technical countermeasures
5. **Historical Dimension** - Historical evolution, intellectual traditions, technological transformation
6. **Related Concepts** - Predecessor concepts, parallel concepts, conceptual relationships

## Installation & Setup

1. **Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Database Configuration**:
Update `schema.py` with your PostgreSQL connection details.

3. **Run Application**:
```bash
python app.py
```

4. **Access Dashboard**:
Navigate to `http://localhost:8051` in your browser.

## Configuration

### Key Files:
- `config.py` - Application settings and constants
- `schema.py` - Database schema and connection
- `app.py` - Main dashboard application

### Environment Variables:
- `PORT` - Application port (default: 8051)
- Database credentials in `schema.py`

## Performance Features

- **Caching**: In-memory caching for frequently accessed data
- **Progress Indicators**: Real-time feedback for long-running operations
- **Optimized Queries**: Efficient PostgreSQL queries with proper indexing
- **Responsive Design**: Mobile-friendly interface with adaptive layouts

## Data Export

All tabs support data export in multiple formats:
- **CSV**: Structured data for spreadsheet analysis
- **JSON**: Machine-readable format for API integration

## Technical Stack

- **Frontend**: Dash (Plotly) with Bootstrap CSS
- **Backend**: Python with SQLAlchemy ORM
- **Database**: PostgreSQL with full-text search capabilities
- **Visualizations**: Plotly charts and custom components
- **Deployment**: Heroku-ready with Gunicorn

## Development

### Project Structure:
```
cognitive-warfare-comparison/
├── app.py                 # Main application
├── config.py             # Configuration
├── schema.py             # Database schema
├── components/           # Reusable UI components
├── database/            # Data fetching and connection utilities
├── tabs/               # Individual tab implementations
├── utils/              # Helper functions and utilities
├── visualizations/     # Chart and graph components
└── static/            # CSS and static assets
```

### Adding New Features:
1. Create new components in appropriate directories
2. Register callbacks in respective tab files
3. Update configuration as needed
4. Test with sample data

## License

This project is developed for academic and research purposes.

## Support

For issues and questions, please refer to the project documentation or contact the development team.