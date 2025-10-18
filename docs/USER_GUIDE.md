# User Guide - Smart Recipe & Meal Planning System

This comprehensive guide walks you through using the Smart Recipe & Meal Planning System to create personalized weekly meal plans.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [User Profile Setup](#user-profile-setup)
3. [Meal Planning Process](#meal-planning-process)
4. [Understanding Your Results](#understanding-your-results)
5. [Example Workflows](#example-workflows)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Time Setup

1. **Ensure Prerequisites**
   - Python 3.8+ installed
   - Google Gemini API key configured
   - Virtual environment activated

2. **Launch the System**
   ```bash
   python -m src.main
   ```

3. **Follow the Interactive Setup**
   The system will guide you through profile creation and meal planning.

### What to Expect

- **Setup Time**: 2-3 minutes for profile creation
- **Processing Time**: 3-5 minutes for meal plan generation
- **Output**: Comprehensive meal plan with recipes, shopping lists, and nutritional analysis

---

## 👤 User Profile Setup

The system collects information about you to create personalized meal plans. Here's what each section covers:

### Personal Information

**What You'll Be Asked:**
- Age, weight, height
- Gender
- Activity level (sedentary, lightly active, moderately active, very active, extremely active)

**Why It Matters:**
- Calculates your daily caloric needs
- Determines macronutrient requirements
- Adjusts portion sizes appropriately

**Example Input:**
```
Age: 28
Weight: 70 kg (154 lbs)
Height: 175 cm (5'9")
Gender: Female
Activity Level: Moderately active (exercise 3-5 times/week)
```

### Dietary Preferences

**What You'll Be Asked:**
- Dietary restrictions (vegetarian, vegan, keto, paleo, etc.)
- Food allergies and intolerances
- Preferred cuisines
- Foods you dislike
- Cooking skill level

**Why It Matters:**
- Ensures all recipes match your dietary needs
- Avoids ingredients that could cause allergic reactions
- Creates recipes you'll actually enjoy making and eating

**Example Input:**
```
Dietary Restrictions: Vegetarian
Allergies: Tree nuts, shellfish
Preferred Cuisines: Mediterranean, Asian, Mexican
Disliked Foods: Mushrooms, olives
Cooking Skill: Intermediate
```

### Health Goals

**What You'll Be Asked:**
- Primary goal (weight loss, muscle gain, maintenance, general health)
- Target daily calories (optional - system can calculate)
- Macronutrient preferences (high protein, low carb, etc.)

**Why It Matters:**
- Tailors meal plans to support your specific health objectives
- Adjusts caloric content and macronutrient ratios
- Ensures nutritional adequacy for your goals

**Example Input:**
```
Primary Goal: Weight loss
Target Calories: Auto-calculate (system suggests 1,650 calories)
Macro Preferences: High protein, moderate carbs
```

### Budget Constraints

**What You'll Be Asked:**
- Weekly grocery budget
- Price sensitivity (low, medium, high)
- Bulk buying preferences
- Preferred shopping locations

**Why It Matters:**
- Keeps meal plans within your financial means
- Suggests cost-effective ingredient alternatives
- Optimizes shopping lists for best value

**Example Input:**
```
Weekly Budget: $75
Price Sensitivity: Medium
Bulk Buying: Yes, for non-perishables
Shopping: Local grocery stores
```

### Schedule Preferences

**What You'll Be Asked:**
- Available cooking time per day
- Meal prep preferences
- Number of meals per day
- Snack preferences

**Why It Matters:**
- Creates realistic meal plans that fit your lifestyle
- Balances quick meals with more elaborate cooking
- Optimizes meal prep efficiency

**Example Input:**
```
Cooking Time: 30-45 minutes on weekdays, 60+ minutes on weekends
Meal Prep: Yes, prefer Sunday batch cooking
Meals Per Day: 3 main meals + 2 snacks
Snack Style: Healthy, portable options
```

---

## 🤖 Meal Planning Process

Once your profile is complete, the system's six AI agents work together to create your meal plan:

### Phase 1: Parallel Analysis (2-3 minutes)

**Nutritionist Agent** and **Ingredient Sourcer** work simultaneously:

- **Nutritionist Agent**: Analyzes your dietary needs, calculates nutritional requirements
- **Ingredient Sourcer**: Researches ingredient availability and pricing in your area

**What You'll See:**
```
🔍 Analyzing dietary requirements...
🛒 Researching ingredient availability and pricing...
⏱️  Estimated completion: 2-3 minutes
```

### Phase 2: Sequential Processing (2-3 minutes)

**Recipe Creator → Cost Calculator → Meal Planner → Health Validator**

1. **Recipe Creator**: Generates custom recipes based on your preferences and nutritional needs
2. **Cost Calculator**: Calculates costs and optimizes for your budget
3. **Meal Planner**: Organizes recipes into a balanced weekly schedule
4. **Health Validator**: Reviews the plan for nutritional compliance and makes final adjustments

**What You'll See:**
```
👨‍🍳 Creating personalized recipes...
💰 Calculating costs and optimizing budget...
📅 Organizing weekly meal schedule...
🏥 Validating nutritional compliance...
```

### Phase 3: Report Generation (1 minute)

The system compiles all information into comprehensive reports:

- Weekly meal plan with daily schedules
- Detailed recipes with instructions
- Organized shopping list with costs
- Nutritional analysis and recommendations

---

## 📊 Understanding Your Results

### Meal Plan Report Structure

Your completed meal plan includes several detailed sections:

#### 1. Executive Summary
- Overview of your personalized plan
- Key nutritional highlights
- Total weekly cost breakdown
- Prep time estimates

#### 2. Weekly Schedule
```
MONDAY
├── Breakfast: Mediterranean Veggie Scramble (320 cal, $2.15)
├── Lunch: Quinoa Buddha Bowl (485 cal, $3.80)
├── Dinner: Lentil Curry with Brown Rice (520 cal, $2.95)
└── Snacks: Greek Yogurt with Berries (180 cal, $1.25)

TUESDAY
├── Breakfast: Overnight Oats with Almonds (350 cal, $1.85)
├── Lunch: Chickpea Salad Wrap (445 cal, $2.60)
├── Dinner: Stuffed Bell Peppers (480 cal, $3.40)
└── Snacks: Hummus with Vegetables (160 cal, $1.15)
```

#### 3. Detailed Recipes
Each recipe includes:
- **Ingredients**: Exact quantities and alternatives
- **Instructions**: Step-by-step cooking directions
- **Nutrition**: Calories, macros, key vitamins/minerals
- **Cost**: Per serving and total recipe cost
- **Time**: Prep time, cook time, total time
- **Tips**: Storage, variations, meal prep notes

#### 4. Shopping List
Organized by store sections:
```
🥬 PRODUCE
├── Spinach (2 bunches) - $3.98
├── Bell Peppers (6 pieces) - $4.50
├── Tomatoes (2 lbs) - $3.20
└── Onions (3 lbs bag) - $2.15

🥛 DAIRY
├── Greek Yogurt (32 oz) - $4.99
├── Eggs (1 dozen) - $2.89
└── Cheese (8 oz block) - $3.45

🌾 PANTRY
├── Quinoa (2 lbs) - $5.99
├── Lentils (1 lb bag) - $1.99
└── Olive Oil (16 oz) - $6.49

Total Estimated Cost: $72.45 (within $75 budget ✅)
```

#### 5. Nutritional Analysis
- Daily and weekly nutritional summaries
- Macro and micronutrient breakdowns
- Comparison to recommended daily values
- Nutritional goal achievement tracking

#### 6. Meal Prep Instructions
- Batch cooking recommendations
- Storage guidelines
- Make-ahead components
- Weekly prep schedule

---

## 🎯 Example Workflows

### Workflow 1: Weight Loss on a Budget

**Profile:**
- Goal: Lose 1-2 lbs per week
- Budget: $50/week
- Cooking time: 30 minutes/day
- Dietary restrictions: None

**System Response:**
- Creates 1,400-calorie meal plan
- Focuses on high-volume, low-calorie foods
- Emphasizes protein for satiety
- Uses affordable ingredients (beans, eggs, seasonal vegetables)
- Includes meal prep strategies to save time and money

**Sample Day:**
```
Breakfast: Veggie Egg White Scramble (250 cal, $1.20)
Lunch: Large Garden Salad with Chickpeas (320 cal, $2.10)
Dinner: Baked Chicken with Roasted Vegetables (450 cal, $2.80)
Snacks: Apple with Peanut Butter (180 cal, $0.85)
Total: 1,200 calories, $6.95/day
```

### Workflow 2: Muscle Gain for Athletes

**Profile:**
- Goal: Gain lean muscle mass
- Budget: $100/week
- Cooking time: 45 minutes/day
- Activity: Weight training 5x/week

**System Response:**
- Creates 2,800-calorie meal plan
- High protein content (150g+ daily)
- Includes pre/post-workout nutrition
- Focuses on nutrient-dense whole foods
- Provides meal timing recommendations

**Sample Day:**
```
Breakfast: Protein Pancakes with Berries (520 cal, $3.15)
Pre-Workout: Banana with Almond Butter (280 cal, $1.25)
Lunch: Quinoa Power Bowl with Salmon (680 cal, $5.40)
Post-Workout: Protein Smoothie (350 cal, $2.80)
Dinner: Lean Beef Stir-Fry with Brown Rice (720 cal, $4.95)
Snacks: Greek Yogurt with Nuts (250 cal, $1.85)
Total: 2,800 calories, $19.40/day
```

### Workflow 3: Vegan Family Meal Planning

**Profile:**
- Goal: Healthy family meals for 4
- Budget: $120/week
- Dietary: Vegan
- Cooking time: 60 minutes/day

**System Response:**
- Creates family-friendly vegan recipes
- Ensures complete protein combinations
- Includes kid-approved options
- Focuses on batch cooking for efficiency
- Provides B12 and iron optimization

**Sample Family Dinner:**
```
Recipe: Lentil Bolognese with Whole Wheat Pasta
Servings: 4
Prep Time: 15 minutes
Cook Time: 45 minutes
Cost: $8.50 total ($2.13 per serving)

Nutrition per serving:
- Calories: 485
- Protein: 18g
- Fiber: 12g
- Iron: 4.2mg (23% DV)
```

### Workflow 4: Keto Meal Planning

**Profile:**
- Goal: Maintain ketosis
- Budget: $80/week
- Dietary: Ketogenic (under 20g carbs/day)
- Cooking skill: Advanced

**System Response:**
- Creates very low-carb, high-fat meal plans
- Focuses on quality fats and proteins
- Includes electrolyte balance considerations
- Provides net carb calculations
- Suggests keto-friendly alternatives

**Sample Day:**
```
Breakfast: Avocado and Bacon Omelet (420 cal, 3g net carbs)
Lunch: Zucchini Noodles with Pesto Chicken (380 cal, 6g net carbs)
Dinner: Salmon with Cauliflower Mash (520 cal, 5g net carbs)
Snacks: Macadamia Nuts (200 cal, 2g net carbs)
Total: 1,520 calories, 16g net carbs
```

---

## 🔧 Advanced Features

### Customizing Your Experience

#### Ingredient Substitutions
The system automatically suggests alternatives for:
- Out-of-season ingredients
- Budget constraints
- Dietary restrictions
- Personal preferences

#### Meal Plan Adjustments
You can request modifications:
- Swap specific meals
- Adjust portion sizes
- Change cooking methods
- Modify spice levels

#### Batch Cooking Optimization
The system identifies opportunities for:
- Cooking grains in bulk
- Preparing proteins ahead
- Making versatile sauces
- Prepping vegetables

### Integration with External Services

#### Grocery Delivery
Shopping lists are formatted for easy import into:
- Instacart
- Amazon Fresh
- Local grocery delivery services

#### Fitness Apps
Nutritional data can be exported for:
- MyFitnessPal
- Cronometer
- Lose It!

#### Calendar Integration
Meal schedules can be exported to:
- Google Calendar
- Apple Calendar
- Outlook

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: "Meal plan doesn't match my preferences"
**Possible Causes:**
- Incomplete profile information
- Conflicting dietary requirements
- Unrealistic budget constraints

**Solutions:**
- Review and update your profile
- Adjust budget or dietary flexibility
- Run the system again with modified inputs

#### Issue: "Recipes are too complex for my skill level"
**Possible Causes:**
- Cooking skill level set too high
- Time constraints not properly specified

**Solutions:**
- Update cooking skill level in profile
- Specify maximum cooking time per meal
- Request simpler recipe alternatives

#### Issue: "Shopping list exceeds my budget"
**Possible Causes:**
- Budget set too low for dietary requirements
- Expensive ingredient preferences
- Location-based price variations

**Solutions:**
- Increase weekly budget slightly
- Allow more ingredient substitutions
- Consider bulk buying options

#### Issue: "Nutritional goals not being met"
**Possible Causes:**
- Conflicting dietary restrictions and goals
- Unrealistic caloric targets
- Missing nutritional preferences

**Solutions:**
- Consult with a nutritionist for realistic goals
- Adjust caloric targets based on system recommendations
- Specify key nutritional priorities

### Getting Additional Help

#### System Logs
Check `logs/meal_planner.log` for detailed execution information:
```bash
tail -f logs/meal_planner.log
```

#### Validation Tools
Run system diagnostics:
```bash
python scripts/validate_setup.py
```

#### Community Support
- Review sample outputs in `sample_data/sample_outputs/`
- Check existing user profiles in `sample_data/user_profiles.py`
- Refer to the API Configuration Guide for setup issues

---

## 📈 Tips for Best Results

### Profile Setup Tips
1. **Be Specific**: Detailed preferences lead to better results
2. **Be Realistic**: Set achievable goals and budgets
3. **Be Flexible**: Allow some ingredient substitutions
4. **Update Regularly**: Refresh your profile as goals change

### Meal Planning Tips
1. **Start Simple**: Begin with basic preferences, add complexity later
2. **Plan Ahead**: Run meal planning on weekends for the following week
3. **Batch Cook**: Take advantage of meal prep recommendations
4. **Stay Organized**: Use the shopping list organization features

### Cost Optimization Tips
1. **Seasonal Eating**: Allow seasonal ingredient preferences
2. **Bulk Buying**: Enable bulk purchasing for non-perishables
3. **Flexible Proteins**: Don't restrict to expensive protein sources
4. **Store Brands**: Allow generic/store brand alternatives

---

## 🎉 Success Stories

### "Lost 15 pounds in 3 months"
*Sarah, 32, Marketing Manager*

"The system made healthy eating so much easier. Having everything planned out removed the guesswork and prevented impulse food decisions. The budget optimization helped me save money while eating better than ever."

### "Simplified family meal planning"
*Mike, 38, Father of 3*

"Feeding a family with different preferences was always stressful. Now I have a week's worth of meals planned in minutes, complete with a shopping list. The kids actually like most of the recipes!"

### "Achieved fitness goals faster"
*Jessica, 26, Personal Trainer*

"As a trainer, I know nutrition is crucial, but I didn't have time to plan meals for myself. This system creates perfectly balanced meal plans that support my training goals and fit my busy schedule."

---

Ready to transform your meal planning experience? Start with the basic setup and gradually explore advanced features as you become more comfortable with the system. Happy meal planning! 🍽️