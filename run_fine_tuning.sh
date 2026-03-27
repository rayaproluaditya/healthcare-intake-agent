#!/bin/bash

echo "🚀 CLINICAL FINE-TUNING SETUP"
echo "=============================="
echo ""

# Step 1: Create training data
echo "1. Creating training examples..."
python -c "
import json
import os

os.makedirs('./data/training_data', exist_ok=True)

examples = {
  'examples': [
    {
      'category': 'headache',
      'input': 'I have a headache',
      'output': 'Thank you for sharing that. To better understand your headache, could you tell me:\n1. When did it start?\n2. Where exactly do you feel the pain?\n3. On a scale of 1-10, how severe is it?\n4. Is it throbbing, sharp, or pressure-like?',
      'tone': 'empathetic'
    },
    {
      'category': 'chest_pain',
      'input': 'I have chest pain',
      'output': 'Thank you for telling me about your chest pain. For safety, I need to ask:\n1. Is the pain accompanied by shortness of breath?\n2. Are you sweating?\n3. Does the pain spread to your arm, jaw, or back?\n\n⚠️ If you are experiencing any of these, please seek immediate medical attention.',
      'tone': 'emergency'
    }
  ]
}

with open('./data/training_data/clinical_examples.json', 'w') as f:
    json.dump(examples, f, indent=2)
print('✅ Created training examples')
"

# Step 2: Run fine-tuning pipeline
echo ""
echo "2. Running fine-tuning pipeline..."
python app/fine_tuning/fine_tune_pipeline.py

# Step 3: Apply fine-tuned prompt to agent
echo ""
echo "3. Applying fine-tuned prompt to agent..."
python scripts/apply_fine_tuning.py

# Step 4: Restart backend
echo ""
echo "4. Restart backend to apply changes..."
echo "   Please restart your backend manually:"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""

# Step 5: Run evaluation
echo "5. After restarting backend, run evaluation:"
echo "   python scripts/evaluate_clinical_tone.py"
echo ""

echo "✅ Fine-tuning complete!"