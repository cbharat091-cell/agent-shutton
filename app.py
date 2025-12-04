"""
Enhanced Flask web application for Agent Shutton with real AI integration.
Supports multiple specialist roles: Writer, Code Expert, Editor, Planner
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import sys
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure environment for AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

try:
    import google.generativeai as genai
    from blogger_agent.config import config
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google.generativeai not available. Install with: pip install google-generativeai")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Store conversation history
conversation_history = []
current_specialist = "General Assistant"

# Define specialist prompts
SPECIALIST_PROMPTS = {
    "writer": """You are an expert technical blog writer. Your role is to:
- Create engaging blog post content
- Structure content with clear headings and sections
- Write in a clear, professional tone
- Include practical examples
- Make complex topics accessible
When asked to write, provide well-structured, high-quality content.""",

    "code_expert": """You are an expert software engineer and coding specialist. Your role is to:
- Provide code examples and explanations
- Debug code and suggest improvements
- Explain programming concepts clearly
- Recommend best practices
- Help with architecture and design patterns
When asked about code, provide working examples with detailed explanations.""",

    "editor": """You are an expert content editor and reviewer. Your role is to:
- Review and improve existing content
- Check for grammar, clarity, and flow
- Suggest improvements to structure
- Enhance readability
- Maintain consistent tone
When asked to edit, provide constructive feedback with specific improvements.""",

    "planner": """You are an expert content planner and strategist. Your role is to:
- Create comprehensive blog post outlines
- Plan content structure and flow
- Suggest topics and angles
- Develop content strategy
- Organize ideas logically
When asked to plan, provide detailed outlines and content strategies.""",
}


def init_genai():
    """Initialize Google GenAI if API key is available."""
    if not GENAI_AVAILABLE:
        return False
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False


async def get_ai_response(prompt: str, specialist: str = "General Assistant") -> str:
    """Get response from Google Gemini AI with streaming support."""
    if not GENAI_AVAILABLE:
        return get_fallback_response(prompt, specialist)
    
    try:
        model = genai.GenerativeModel(config.worker_model if hasattr(config, 'worker_model') else "gemini-2.5-flash")
        
        # Build the full prompt with specialist context
        specialist_prompt = SPECIALIST_PROMPTS.get(specialist.lower().replace(" ", "_"), SPECIALIST_PROMPTS.get("writer", ""))
        full_prompt = f"{specialist_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error calling GenAI: {e}")
        return get_fallback_response(prompt, specialist)


def get_fallback_response(prompt: str, specialist: str = "General Assistant") -> str:
    """Provide fallback response when AI is not available."""
    fallback_responses = {
        "writer": f"""As a Technical Writer, I understand you want to: {prompt}

I can help you create:
✓ Blog post outlines with clear structure
✓ Well-formatted technical content
✓ Engaging introductions and conclusions
✓ Code examples with explanations
✓ Publication-ready articles

To enable real AI responses, please set the GOOGLE_API_KEY environment variable.

Note: Currently running in fallback mode. For full AI capabilities, add your Google Gemini API key.""",

        "code_expert": f"""As a Code Expert, regarding: {prompt}

I can assist with:
✓ Writing and reviewing code
✓ Debugging and optimization
✓ Design patterns and architecture
✓ Best practices and standards
✓ Performance improvements

To enable real AI responses, please set the GOOGLE_API_KEY environment variable.""",

        "editor": f"""As a Content Editor, for: {prompt}

I can help you:
✓ Review and improve content
✓ Enhance clarity and flow
✓ Fix grammar and style issues
✓ Strengthen structure
✓ Polish for publication

To enable real AI responses, please set the GOOGLE_API_KEY environment variable.""",

        "planner": f"""As a Content Planner, regarding: {prompt}

I can create:
✓ Detailed blog post outlines
✓ Content strategy plans
✓ Topic organization
✓ Section breakdowns
✓ Flow and structure

To enable real AI responses, please set the GOOGLE_API_KEY environment variable.""",
    }
    
    specialist_key = specialist.lower().replace(" ", "_")
    if specialist_key in fallback_responses:
        return fallback_responses[specialist_key]
    
    return f"""I'm an AI Assistant. You asked: {prompt}

I can help as:
- **Writer**: Create blog content
- **Code Expert**: Help with programming
- **Editor**: Review and improve content
- **Planner**: Outline and strategize

Note: For full AI capabilities, please set the GOOGLE_API_KEY environment variable."""


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/agent-info', methods=['GET'])
def get_agent_info():
    """Get information about the agent."""
    from blogger_agent.agent import interactive_blogger_agent
    return jsonify({
        'name': interactive_blogger_agent.name,
        'description': interactive_blogger_agent.description,
        'specialists': list(SPECIALIST_PROMPTS.keys()),
        'genai_available': GENAI_AVAILABLE,
        'current_specialist': current_specialist,
    })


@app.route('/api/specialists', methods=['GET'])
def get_specialists():
    """Get list of available specialist roles."""
    return jsonify({
        'specialists': [
            {'id': 'writer', 'name': 'Blog Writer', 'emoji': '✍️', 'description': 'Writes engaging blog content'},
            {'id': 'code_expert', 'name': 'Code Expert', 'emoji': '💻', 'description': 'Helps with programming'},
            {'id': 'editor', 'name': 'Editor', 'emoji': '📝', 'description': 'Reviews and improves content'},
            {'id': 'planner', 'name': 'Planner', 'emoji': '📋', 'description': 'Plans content strategy'},
        ]
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI."""
    global current_specialist
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    specialist = data.get('specialist', 'writer').lower()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Update current specialist
    current_specialist = specialist.replace('_', ' ').title()
    
    # Add user message to history
    conversation_history.append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat(),
        'specialist': current_specialist
    })
    
    try:
        # Get AI response (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_response = loop.run_until_complete(get_ai_response(user_message, specialist))
        loop.close()
        
        # Add agent response to history
        conversation_history.append({
            'role': 'assistant',
            'content': agent_response,
            'timestamp': datetime.now().isoformat(),
            'specialist': current_specialist
        })
        
        return jsonify({
            'user_message': user_message,
            'agent_response': agent_response,
            'specialist': current_specialist,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Error in chat: {e}")
        return jsonify({'error': error_msg}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history."""
    return jsonify({'history': conversation_history})


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history."""
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'cleared'})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration info."""
    from blogger_agent.config import config
    
    return jsonify({
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
        'location': os.getenv('GOOGLE_CLOUD_LOCATION'),
        'use_vertex_ai': os.getenv('GOOGLE_GENAI_USE_VERTEXAI'),
        'worker_model': getattr(config, 'worker_model', 'gemini-2.5-flash'),
        'critic_model': getattr(config, 'critic_model', 'gemini-2.5-pro'),
        'genai_configured': init_genai(),
        'genai_api_key_set': bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")),
    })


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("Agent Shutton - Enhanced Demo with Real AI")
    print(f"{'='*60}")
    print(f"Status: {'✓ AI Ready' if init_genai() else '✗ AI Not Configured'}")
    print(f"Note: To enable real AI, set GOOGLE_API_KEY environment variable")
    print(f"Server: http://localhost:5000")
    print(f"{'='*60}\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
