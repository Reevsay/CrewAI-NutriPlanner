# 🤖 CrewAI-NutriPlanner

> **Advanced Multi-Agent AI System for Intelligent Meal Planning**

A sophisticated CrewAI-based system that orchestrates **6 specialized AI agents** to create personalized weekly meal plans with recipes, nutritional analysis, and shopping lists. Built with production-ready architecture, comprehensive error handling, and real-world problem-solving capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-green.svg)](https://github.com/joaomdmoura/crewAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 **What Makes This Special**

This isn't just another meal planner—it's a **sophisticated AI engineering project** that demonstrates:

- ✅ **Advanced Multi-Agent Architecture** using CrewAI framework
- ✅ **Production-Ready Code** with comprehensive error handling & fallback systems  
- ✅ **Real-World Problem Solving** with budget constraints & nutritional optimization
- ✅ **Professional Documentation** and clean, maintainable codebase
- ✅ **Full System Integration** from user input to formatted output reports

## 🌟 Features

- **🤖 Multi-Agent Coordination**: Six specialized AI agents working together seamlessly
- **🍎 Personalized Nutrition**: Tailored to individual dietary needs and health goals
- **💰 Budget Optimization**: Cost-effective meal planning within budget constraints
- **👨‍🍳 Recipe Generation**: Custom recipes based on preferences and nutritional requirements
- **🛒 Smart Shopping Lists**: Organized grocery lists with cost breakdowns and alternatives
- **🏥 Health Validation**: Nutritional compliance checking and meal plan validation
- **📊 Comprehensive Reports**: Detailed nutritional analysis and meal prep instructions

## 👀 **See It In Action**

**🎯 [View Real Output Examples](output_examples/)** - See actual AI-generated meal plans, shopping lists, and nutritional analysis produced by this system.

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Framework** | CrewAI | Multi-agent orchestration & coordination |
| **LLM Integration** | Google Gemini API | Natural language processing & reasoning |
| **Data Models** | Pydantic | Type-safe data validation & serialization |
| **External APIs** | USDA Nutrition, Kroger Price APIs | Real-world data integration |
| **Architecture** | Python 3.8+ | Clean, maintainable, production-ready code |
| **Error Handling** | Custom Fallback Systems | Robust operation even when APIs fail |

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**: Required for running the application
- **Google Gemini API Key**: Free API key for CrewAI agents ([Get yours here](https://makersuite.google.com/app/apikey))
- **Optional APIs**: Nutrition and grocery price APIs for enhanced functionality

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Reevsay/CrewAI-NutriPlanner.git
cd CrewAI-NutriPlanner
```

2. **Create and activate virtual environment:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your API keys (see API Configuration section)
```

### Basic Usage

```bash
# Run the meal planning system
python -m src.main
```

The system will guide you through:
1. **Profile Setup**: Enter your dietary preferences, health goals, and budget
2. **Meal Planning**: AI agents create your personalized meal plan
3. **Report Generation**: Receive detailed recipes, shopping lists, and nutritional analysis

## 📁 Project Structure

```
smart-recipe-meal-planner/
├── src/
│   ├── agents/              # CrewAI agent implementations
│   │   ├── nutritionist.py  # Dietary analysis agent
│   │   ├── recipe_creator.py # Recipe generation agent
│   │   ├── ingredient_sourcer.py # Ingredient research agent
│   │   ├── cost_calculator.py # Budget optimization agent
│   │   ├── meal_planner.py  # Weekly scheduling agent
│   │   └── health_validator.py # Meal plan validation agent
│   ├── tools/               # External API integrations
│   │   ├── nutrition_api.py # USDA/Nutritionix integration
│   │   ├── grocery_price_api.py # Price lookup services
│   │   └── calculation_tools.py # Custom utilities
│   ├── models/              # Data models and schemas
│   │   ├── user_profile.py  # User profile models
│   │   ├── recipe_models.py # Recipe and ingredient models
│   │   └── meal_plan_models.py # Meal plan structures
│   ├── interface/           # User interaction components
│   │   ├── user_input.py    # Profile collection interface
│   │   ├── workflow.py      # Execution orchestration
│   │   └── report_generator.py # Output formatting
│   ├── utils/               # Utility functions
│   │   ├── gemini_config.py # API configuration
│   │   ├── formatters.py    # Output formatting
│   │   └── validators.py    # Input validation
│   ├── workflow/            # CrewAI workflow definitions
│   │   ├── crew_config.py   # Crew setup and coordination
│   │   └── task_definitions.py # Agent task specifications
│   └── main.py              # Application entry point
├── config/                  # Configuration files
│   └── settings.py          # Application settings
├── tests/                   # Comprehensive test suite
├── sample_data/             # Example profiles and outputs
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## ⚙️ Configuration

### Required Configuration

The system requires a **Google Gemini API key** for basic functionality:

1. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file:
```bash
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### Optional APIs for Enhanced Features

For full functionality, configure these optional APIs in your `.env` file:

#### Nutrition APIs
- **USDA FoodData Central** (Free, no key required)
- **Nutritionix** (Paid, more comprehensive data)

#### Grocery Price APIs
- **Kroger API** (Free tier available)
- **Instacart API** (Contact for access)

See the [API Configuration Guide](docs/API_CONFIGURATION.md) for detailed setup instructions.

## 📖 Usage Examples

### Basic Meal Planning
```bash
python -m src.main
```
Follow the interactive prompts to create your meal plan.

### Example User Profiles

The system works with various dietary needs:

- **Weight Loss**: Calorie-controlled meals with high protein
- **Muscle Gain**: High-protein, calorie-dense meal plans
- **Vegetarian/Vegan**: Plant-based nutrition optimization
- **Keto/Low-Carb**: High-fat, low-carbohydrate meal plans
- **Gluten-Free**: Celiac-safe meal planning
- **Budget-Conscious**: Cost-optimized meal plans under $50/week

### Sample Execution Flow

1. **Profile Collection** (2-3 minutes)
   - Personal information (age, weight, height, activity level)
   - Dietary preferences and restrictions
   - Health goals and budget constraints

2. **AI Processing** (3-5 minutes)
   - Nutritionist Agent analyzes dietary needs
   - Recipe Creator generates custom recipes
   - Cost Calculator optimizes budget allocation
   - Meal Planner creates weekly schedule
   - Health Validator ensures compliance

3. **Report Generation** (1 minute)
   - Comprehensive meal plan with recipes
   - Organized shopping list with costs
   - Nutritional analysis and recommendations

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_integration/
pytest tests/test_end_to_end/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Lint code
flake8 src/ tests/
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run in development mode
ENVIRONMENT=development python -m src.main
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your Google Gemini API key is valid
   - Check that the key is properly set in your `.env` file

2. **Installation Issues**
   - Use Python 3.8 or higher
   - Ensure virtual environment is activated
   - Try upgrading pip: `pip install --upgrade pip`

3. **Performance Issues**
   - Check your internet connection for API calls
   - Increase timeout settings in `.env` if needed
   - Monitor logs in `logs/meal_planner.log`

### Getting Help

- Check the [User Guide](docs/USER_GUIDE.md) for detailed usage instructions
- Review logs in the `logs/` directory for error details
- Ensure all required dependencies are installed

## 📚 Documentation

- **[API Configuration Guide](docs/API_CONFIGURATION.md)** - Detailed setup instructions for all APIs
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage examples and workflows  
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and agent coordination
- **[Output Examples](output_examples/)** - Real AI-generated meal plans showcasing system capabilities

### Quick Links
- [Getting Your First API Key](docs/API_CONFIGURATION.md#google-gemini-api-required) - Start here for setup
- [Example Workflows](docs/USER_GUIDE.md#example-workflows) - See the system in action
- [View Sample Output](output_examples/) - See what the AI generates
- [Troubleshooting Guide](docs/USER_GUIDE.md#troubleshooting) - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent coordination
- Powered by [Google Gemini](https://ai.google.dev/) for intelligent meal planning
- Nutritional data from [USDA FoodData Central](https://fdc.nal.usda.gov/)

---

**Ready to transform your meal planning? Get started in minutes with just a free Google Gemini API key!** 🚀