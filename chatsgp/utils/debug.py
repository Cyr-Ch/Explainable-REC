"""Debug utility for logging agent prompts and outputs"""
import os
import json

def _is_debug_enabled():
    """Check if debug is enabled (dynamically checks environment variable)"""
    return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

def debug_print(agent_name, section, content):
    """Print debug information with formatting"""
    if not _is_debug_enabled():
        return
    
    print(f"\n{'='*80}")
    print(f"[DEBUG] {agent_name} - {section}")
    print(f"{'='*80}")
    
    if isinstance(content, dict):
        print(json.dumps(content, indent=2, ensure_ascii=False))
    elif isinstance(content, str):
        # Print long strings with word wrapping
        if len(content) > 200:
            print(content[:200] + "...\n[truncated - full content is very long]")
        else:
            print(content)
    else:
        print(str(content))
    
    print(f"{'='*80}\n")

def debug_prompt(agent_name, prompt):
    """Debug print for prompts"""
    debug_print(agent_name, "PROMPT", prompt)

def debug_response(agent_name, response):
    """Debug print for responses"""
    debug_print(agent_name, "RESPONSE", response)

def debug_data(agent_name, data_name, data):
    """Debug print for data"""
    debug_print(agent_name, f"DATA: {data_name}", data)

