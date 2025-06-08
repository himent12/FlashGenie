# 🤖 AI Content Generation - Test Guide

## ✅ **Quick Test Instructions**

### **1. Start FlashGenie Interactive Shell**
```bash
python -m flashgenie
```

### **2. Test AI Generation with Different Inputs**

#### **Test 1: File Path Input (Should Generate Examples)**
```bash
FlashGenie > generate
# When prompted for text, enter: assets/sample_data/example_deck.csv
# Select content type: 3 (Vocabulary)
# Max cards: 3
# Expected: Should generate example vocabulary cards
```

#### **Test 2: Short Text Input (Should Generate Examples)**
```bash
FlashGenie > generate
# When prompted for text, enter: example_deck
# Select content type: 1 (Facts)
# Max cards: 3
# Expected: Should generate example fact cards
```

#### **Test 3: Proper Educational Content (Should Extract Real Content)**
```bash
FlashGenie > generate
# When prompted for text, enter:
The speed of light is 299,792,458 meters per second.
Water boils at 100 degrees Celsius.
The chemical symbol for gold is Au.
Photosynthesis is the process by which plants make food.

# Select content type: 1 (Facts)
# Max cards: 4
# Expected: Should generate 4 real flashcards from the content
```

#### **Test 4: Vocabulary Content**
```bash
FlashGenie > generate
# When prompted for text, enter:
Hello - A greeting
Thank you - Expression of gratitude
Please - Polite request word
Goodbye - Farewell expression

# Select content type: 3 (Vocabulary)
# Max cards: 4
# Expected: Should generate vocabulary flashcards
```

## 🎯 **Expected Results**

### **File Path/Short Text Inputs**
- Should show helpful warning about file paths
- Should generate example flashcards to demonstrate the feature
- Should provide guidance on proper text input format

### **Proper Content Inputs**
- Should extract real content from the text
- Should create appropriate question-answer pairs
- Should assign relevant tags and difficulty levels
- Should show confidence scores and source information

## 🔧 **Troubleshooting**

### **If No Cards Are Generated**
1. Check that you're providing actual text content, not file paths
2. Try using the example content provided above
3. Make sure the text contains factual statements or definitions

### **If Cards Are Low Quality**
1. Provide more structured text with clear statements
2. Use formats like "X is Y" or "X means Y"
3. Include more context in your input text

## 📊 **Content Type Guidelines**

### **Facts (Type 1)**
Best input format:
- "The speed of light is 299,792,458 m/s"
- "Water boils at 100 degrees Celsius"
- "Paris is the capital of France"

### **Definitions (Type 2)**
Best input format:
- "Photosynthesis is the process by which plants make food"
- "Democracy means government by the people"
- "Gravity is the force that attracts objects"

### **Vocabulary (Type 3)**
Best input format:
- "Hello - A greeting"
- "Bonjour - French word for hello"
- "Gracias - Spanish word meaning thank you"

### **Formulas (Type 4)**
Best input format:
- "Area of circle = πr²"
- "Pythagorean theorem: a² + b² = c²"
- "Speed = distance / time"

### **Questions (Type 5)**
Best input format:
- "What is the capital of France? Paris"
- "Who wrote Romeo and Juliet? Shakespeare"
- "When did WWII end? 1945"

## 🎉 **Success Indicators**

✅ **Working Correctly When:**
- File paths generate example cards with helpful warnings
- Short text generates example cards
- Proper content extracts real flashcards
- Generated cards have appropriate questions and answers
- Cards include relevant tags and difficulty scores
- Rich UI displays progress and results beautifully

❌ **Needs Attention If:**
- No cards are generated from proper content
- Error messages appear during generation
- Rich UI doesn't display properly
- Generated cards have empty questions or answers

---

**The AI Content Generation feature should now work with ANY input type, providing helpful examples when needed and extracting real content when possible!** 🤖✨
