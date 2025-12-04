## Agent Shutton - Enhanced AI Features Guide

### ✨ What's New

Agent Shutton now has **real AI integration** with multiple specialist roles:

#### 🎯 Specialist Roles

1. **✍️ Blog Writer**
   - Creates engaging blog content
   - Structures articles professionally
   - Writes in clear, accessible tone

2. **💻 Code Expert**
   - Provides code examples and explanations
   - Debugs and optimizes code
   - Explains programming concepts

3. **📝 Editor**
   - Reviews and improves content
   - Fixes grammar and style
   - Enhances readability

4. **📋 Planner**
   - Creates detailed outlines
   - Plans content strategy
   - Organizes ideas logically

### 🚀 Getting Started

#### Option 1: With Real AI (Recommended)

1. Get a free Google Gemini API key:
   - Visit https://ai.google.dev/
   - Click "Get API Key"
   - Copy your key

2. Set the environment variable:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

3. Run the app:
   ```bash
   cd /workspaces/agent-shutton
   python app.py
   ```

4. Open http://localhost:5000 in your browser

#### Option 2: Fallback Mode (Works Without API Key)

The app runs in **Fallback Mode** automatically if no API key is set. You'll get:
- ✓ Full UI functionality
- ✓ Real-like responses with helpful structure
- ✗ Not actual AI (useful for testing UI)

### 💬 How to Use

1. **Select a Specialist** - Click the specialist button on the left
2. **Type Your Question** - Ask anything related to your specialist's role
3. **Get Response** - Wait for the AI to respond
4. **Continue Conversation** - Keep asking follow-up questions

### 📝 Example Prompts

**For Blog Writer:**
- "Write a blog post about machine learning"
- "Create content about cloud computing"
- "Help me write about web development"

**For Code Expert:**
- "How do I write a Python decorator?"
- "Explain async/await in JavaScript"
- "Show me a REST API example"

**For Editor:**
- "Edit this blog post: [paste content]"
- "Improve the clarity of this text"
- "Fix grammar and style issues"

**For Planner:**
- "Create an outline for a technical blog"
- "Plan a series of articles about AI"
- "Structure a complete learning guide"

### ⚙️ Configuration

#### Environment Variables

```bash
# Required for real AI
export GOOGLE_API_KEY="your_api_key_here"

# Optional
export GOOGLE_CLOUD_PROJECT="your_project_id"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="False"
```

#### Model Configuration

In `blogger_agent/config.py`:
- `worker_model`: gemini-2.5-flash (fast, good quality)
- `critic_model`: gemini-2.5-pro (higher quality, slower)
- `max_search_iterations`: 5 (for search-based tasks)

### 🐛 Troubleshooting

**"AI Not Configured" status**
- Add your GOOGLE_API_KEY
- Refresh the page after setting the key

**Empty responses**
- Check internet connection
- Verify API key is valid
- Check browser console for errors

**Server not starting**
- Make sure port 5000 is free
- Run: `lsof -i :5000`
- Kill the process if needed: `kill -9 <PID>`

### 🔄 Switching Between Modes

The app automatically detects:
- ✓ **Real AI Mode** - If GOOGLE_API_KEY is set
- ✓ **Fallback Mode** - Without API key (for testing)

Both modes have identical UI, just different response sources.

### 📊 Features

- ✓ Real-time chat interface
- ✓ Multiple specialist roles
- ✓ Conversation history tracking
- ✓ Clear chat functionality
- ✓ Responsive design (desktop & mobile)
- ✓ Loading indicators
- ✓ Error handling

### 🚨 Important Notes

1. **API Usage**: Using real AI will consume API credits
2. **Rate Limiting**: Google Gemini has rate limits
3. **Privacy**: Keep your API key secret!
4. **Testing**: Use fallback mode for UI testing

### 📚 Resources

- Google Gemini API: https://ai.google.dev/
- Blog Agent Docs: See README.md
- ADK Documentation: https://github.com/google/adk

---

Enjoy using Agent Shutton! 🤖✨
