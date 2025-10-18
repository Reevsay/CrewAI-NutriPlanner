# API Configuration Guide

This guide provides detailed instructions for configuring all APIs used by the Smart Recipe & Meal Planning System.

## 🔑 Required APIs

### Google Gemini API (Required)

The Google Gemini API powers all AI agents in the system and is **required** for basic functionality.

#### Setup Instructions

1. **Get Your API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Configure in Environment**
   ```bash
   # Add to your .env file
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

3. **Verify Configuration**
   ```bash
   # Test your configuration
   python -c "from src.utils.gemini_config import configure_gemini; print('✅ Success' if configure_gemini() else '❌ Failed')"
   ```

#### API Limits
- **Free Tier**: 60 requests per minute, 1,500 requests per day
- **Rate Limiting**: Automatically handled by the system
- **Cost**: Free for personal use

---

## 🍎 Nutrition APIs (Optional)

Nutrition APIs provide detailed nutritional information for ingredients and recipes. The system works with basic nutrition data without these APIs, but they enhance accuracy.

### USDA FoodData Central (Recommended - Free)

The USDA API provides comprehensive nutritional data for thousands of foods.

#### Setup Instructions

1. **No API Key Required**
   - The USDA API is free and doesn't require registration
   - Already configured in the system

2. **Configuration**
   ```bash
   # Already set in .env.example
   USDA_API_BASE_URL=https://api.nal.usda.gov/fdc/v1
   ```

3. **Features**
   - 300,000+ food items
   - Detailed nutritional breakdowns
   - No rate limits for reasonable use

### Nutritionix API (Alternative - Paid)

Nutritionix provides more user-friendly food names and restaurant data.

#### Setup Instructions

1. **Get API Credentials**
   - Visit [Nutritionix Developer Portal](https://developer.nutritionix.com/)
   - Create an account and application
   - Get your App ID and API Key

2. **Configure in Environment**
   ```bash
   # Add to your .env file
   NUTRITIONIX_APP_ID=your_nutritionix_app_id_here
   NUTRITIONIX_API_KEY=your_nutritionix_api_key_here
   ```

3. **Features**
   - Restaurant and brand foods
   - Natural language food queries
   - 500 requests/day (free tier)

---

## 🛒 Grocery Price APIs (Optional)

Grocery APIs provide real-time pricing and availability data. The system can estimate costs without these APIs.

### Kroger API (Recommended)

Kroger provides pricing data for their stores across the US.

#### Setup Instructions

1. **Developer Registration**
   - Visit [Kroger Developer Portal](https://developer.kroger.com/)
   - Create a developer account
   - Register a new application
   - Get Client ID and Client Secret

2. **Configure in Environment**
   ```bash
   # Add to your .env file
   KROGER_CLIENT_ID=your_kroger_client_id_here
   KROGER_CLIENT_SECRET=your_kroger_client_secret_here
   ```

3. **Features**
   - Real-time pricing data
   - Store location-based pricing
   - Product availability information

### Instacart API (Enterprise)

Instacart provides comprehensive grocery data but requires business partnership.

#### Setup Instructions

1. **Business Partnership Required**
   - Contact Instacart for API access
   - Requires business use case and approval

2. **Configuration**
   ```bash
   # Add to your .env file (if approved)
   INSTACART_API_KEY=your_instacart_api_key_here
   ```

---

## ⚙️ Configuration File Reference

### Complete .env Configuration

```bash
# ============================================
# REQUIRED CONFIGURATION
# ============================================

# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# ============================================
# OPTIONAL NUTRITION APIS
# ============================================

# USDA FoodData Central API (Free - no key required)
USDA_API_BASE_URL=https://api.nal.usda.gov/fdc/v1

# Nutritionix API (Optional - paid service)
NUTRITIONIX_APP_ID=your_nutritionix_app_id_here
NUTRITIONIX_API_KEY=your_nutritionix_api_key_here

# ============================================
# OPTIONAL GROCERY PRICE APIS
# ============================================

# Kroger API (Optional)
KROGER_CLIENT_ID=your_kroger_client_id_here
KROGER_CLIENT_SECRET=your_kroger_client_secret_here

# Instacart API (Optional - enterprise only)
INSTACART_API_KEY=your_instacart_api_key_here

# ============================================
# APPLICATION CONFIGURATION
# ============================================

# Logging Configuration
LOG_LEVEL=INFO

# API Configuration
CACHE_DURATION_HOURS=24
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Development Settings
DEBUG=False
ENVIRONMENT=production
```

### Minimal Configuration (Free APIs Only)

For basic functionality with free APIs only:

```bash
# Minimal .env configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here
USDA_API_BASE_URL=https://api.nal.usda.gov/fdc/v1
LOG_LEVEL=INFO
```

---

## 🔧 Configuration Validation

### Automatic Validation

The system automatically validates your configuration on startup:

```bash
python -m src.main
```

Look for these messages:
- ✅ `Configuration validated successfully` - All required APIs configured
- ⚠️ `Optional APIs not configured` - System will work with reduced functionality
- ❌ `Google Gemini API key is required` - Missing required configuration

### Manual Validation

Test individual API configurations:

```bash
# Test Gemini API
python -c "from src.utils.gemini_config import configure_gemini; configure_gemini()"

# Test Nutrition APIs
python -c "from src.tools.nutrition_api import NutritionAPI; api = NutritionAPI(); print(api.test_connection())"

# Test Grocery APIs
python -c "from src.tools.grocery_price_api import GroceryPriceAPI; api = GroceryPriceAPI(); print(api.test_connection())"
```

---

## 🚨 Troubleshooting

### Common Configuration Issues

#### 1. Invalid Google Gemini API Key
```
Error: Failed to configure Gemini API. Please check your API key.
```
**Solution:**
- Verify your API key is correct
- Ensure no extra spaces in the .env file
- Check that the API key is active in Google AI Studio

#### 2. API Rate Limiting
```
Error: Rate limit exceeded for API calls
```
**Solution:**
- Wait for rate limit reset (usually 1 minute)
- Consider upgrading to paid API tiers
- The system automatically handles retries

#### 3. Network Connection Issues
```
Error: Failed to connect to API endpoint
```
**Solution:**
- Check your internet connection
- Verify firewall settings allow API calls
- Try increasing REQUEST_TIMEOUT in .env

#### 4. Missing .env File
```
Error: Environment variables not found
```
**Solution:**
- Ensure .env file exists in project root
- Copy from .env.example: `cp .env.example .env`
- Add your API keys to the .env file

### Getting API Keys

| API | Cost | Registration | Time to Setup |
|-----|------|-------------|---------------|
| Google Gemini | Free | Google Account | 2 minutes |
| USDA FoodData | Free | None Required | 0 minutes |
| Nutritionix | Free Tier | Email Registration | 5 minutes |
| Kroger | Free | Developer Account | 10 minutes |
| Instacart | Enterprise | Business Partnership | Weeks |

### Support Resources

- **Google Gemini**: [AI Studio Documentation](https://ai.google.dev/docs)
- **USDA API**: [FoodData Central API Guide](https://fdc.nal.usda.gov/api-guide.html)
- **Nutritionix**: [Developer Documentation](https://docs.nutritionix.com/)
- **Kroger**: [Developer Portal](https://developer.kroger.com/documentation)

---

## 🎯 Recommended Setup

For the best experience, we recommend this configuration priority:

1. **Start with Minimal** (Free)
   - Google Gemini API
   - USDA Nutrition API

2. **Add Enhanced Nutrition** (Optional)
   - Nutritionix API for better food recognition

3. **Add Price Data** (Optional)
   - Kroger API for real-time pricing

This approach lets you start immediately with free APIs and add paid services as needed.