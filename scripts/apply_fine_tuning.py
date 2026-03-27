#!/usr/bin/env python3
"""
Apply fine-tuned clinical prompt to the agent
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_fine_tuning():
    """Update the agent's system prompt with fine-tuned version"""
    
    # Path to the fine-tuned prompt
    prompt_path = "./data/training_data/clinical_system_prompt.txt"
    
    if not os.path.exists(prompt_path):
        print("❌ Fine-tuned prompt not found. Run fine_tune_pipeline.py first.")
        return False
    
    # Read the fine-tuned prompt
    with open(prompt_path, 'r') as f:
        fine_tuned_prompt = f.read()
    
    # Path to agent file
    agent_path = "./app/agents/intake_agent.py"
    
    if not os.path.exists(agent_path):
        print(f"❌ Agent file not found at {agent_path}")
        return False
    
    # Read current agent file
    with open(agent_path, 'r') as f:
        agent_content = f.read()
    
    # Find the system prompt section and replace it
    import re
    
    # Pattern to find the system prompt assignment
    pattern = r'self\.system_prompt = """(.*?)"""'
    
    # Replace with fine-tuned prompt
    new_content = re.sub(
        pattern,
        f'self.system_prompt = """{fine_tuned_prompt}"""',
        agent_content,
        flags=re.DOTALL
    )
    
    # Backup original
    backup_path = f"{agent_path}.backup"
    with open(backup_path, 'w') as f:
        f.write(agent_content)
    print(f"✅ Backed up original agent to {backup_path}")
    
    # Write updated content
    with open(agent_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Applied fine-tuned clinical prompt to agent!")
    print("\nChanges applied:")
    print(f"  - System prompt updated with {len(fine_tuned_prompt)} characters")
    print(f"  - Original backed up to {backup_path}")
    
    return True

if __name__ == "__main__":
    apply_fine_tuning()