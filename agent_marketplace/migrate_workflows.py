#!/usr/bin/env python3
"""
Migration script to move workflows from saved_workflows.json to n8n_workflows.json
This ensures the marketplace reads from the proper database format.
"""

import json
import os
import uuid
from datetime import datetime

def migrate_workflows():
    """Migrate workflows from saved_workflows.json to n8n_workflows.json"""
    
    saved_workflows_file = 'saved_workflows.json'
    n8n_workflows_file = 'n8n_workflows.json'
    
    if not os.path.exists(saved_workflows_file):
        print("No saved_workflows.json file found - nothing to migrate")
        return
    
    # Load existing saved workflows
    try:
        with open(saved_workflows_file, 'r') as f:
            saved_workflows = json.load(f)
    except Exception as e:
        print(f"Error reading saved_workflows.json: {e}")
        return
    
    # Load existing n8n workflows (if any)
    n8n_workflows = []
    if os.path.exists(n8n_workflows_file):
        try:
            with open(n8n_workflows_file, 'r') as f:
                n8n_workflows = json.load(f)
        except:
            n8n_workflows = []
    
    # Track existing template IDs to avoid duplicates
    existing_template_ids = set()
    for workflow in n8n_workflows:
        template_id = workflow.get('template_id')
        if template_id:
            existing_template_ids.add(str(template_id))
    
    migrated_count = 0
    
    # Process each workflow from saved_workflows.json
    for workflow in saved_workflows:
        template_id = workflow.get('template_id')
        name = workflow.get('name', 'Unknown Workflow')
        
        # Only migrate workflows that look like marketplace templates
        is_marketplace = (
            (template_id and str(template_id).isdigit()) or  # Numeric template ID
            workflow.get('source') == 'n8n_template' or     # Explicitly marked
            workflow.get('id', '').startswith('n8n-')       # ID starts with 'n8n-'
        )
        
        if is_marketplace and template_id and str(template_id) not in existing_template_ids:
            # Convert to database format
            workflow_entry = {
                'id': str(uuid.uuid4()),
                'user_id': None,  # No user_id for marketplace templates
                'template_id': str(template_id),
                'template_url': f"https://n8n.io/workflows/{template_id}",
                'workflow_name': name,
                'workflow_description': workflow.get('description', f"N8N workflow template (Template ID: {template_id})"),
                'workflow_json': '{}',  # Placeholder - would need actual workflow data
                'n8n_workflow_id': None,
                'credentials_required': json.dumps([]),
                'created_at': workflow.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'source': 'n8n_marketplace'
            }
            
            n8n_workflows.append(workflow_entry)
            existing_template_ids.add(str(template_id))
            migrated_count += 1
            print(f"Migrated workflow: {name} (ID: {template_id})")
    
    # Save the updated n8n_workflows
    try:
        with open(n8n_workflows_file, 'w') as f:
            json.dump(n8n_workflows, f, indent=2)
        
        print(f"✅ Successfully migrated {migrated_count} workflows to {n8n_workflows_file}")
        print(f"Total workflows in database: {len(n8n_workflows)}")
        
    except Exception as e:
        print(f"Error saving to {n8n_workflows_file}: {e}")

if __name__ == '__main__':
    migrate_workflows() 