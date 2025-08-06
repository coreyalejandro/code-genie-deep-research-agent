# 🌐 Browser Extension Installation

## Install Your Deep Research Agent Extension

### Chrome/Edge Installation:

1. **Download the Extension**
   ```bash
   # The extension files are in the browser_extension/ directory
   cd browser_extension
   ```

2. **Open Chrome/Edge**
   - Go to `chrome://extensions/` (Chrome) or `edge://extensions/` (Edge)
   - Enable "Developer mode" (toggle in top right)

3. **Load Extension**
   - Click "Load unpacked"
   - Select the `browser_extension` folder
   - Your extension should now appear in the extensions list

4. **Pin the Extension**
   - Click the puzzle piece icon in the toolbar
   - Find "Deep Research Agent" and click the pin icon

### Firefox Installation:

1. **Open Firefox**
   - Go to `about:debugging`
   - Click "This Firefox"
   - Click "Load Temporary Add-on"

2. **Select Manifest**
   - Navigate to the `browser_extension` folder
   - Select `manifest.json`

## 🚀 Using Your Extension

### Popup Interface:
- Click the extension icon in your toolbar
- Use the popup to:
  - Open research sidebar
  - Analyze current page
  - Save to notebook
  - Ask research questions

### Sidebar Interface:
- Click "Open Research Sidebar" in the popup
- A sidebar will appear on the current page
- Chat with your research agent about the page content

### Keyboard Shortcuts:
- `Ctrl+Shift+R` - Open research sidebar (can be configured)

## 🔧 Configuration

### Connect to Your Local Agent:
The extension tries to connect to your local research agent at `http://localhost:8000`

Make sure your agent is running:
```bash
research julius  # Start Julius agent
# or
research notebook  # Start enhanced notebook
```

### Customize Settings:
- Right-click the extension icon
- Select "Options" (if available)
- Configure API endpoints and preferences

## 🎯 Features

### Everywhere Access:
- **Any webpage** - Your agent can analyze any page you visit
- **Context awareness** - Agent knows what page you're on
- **Seamless integration** - Works like Sider but with your own agent

### Research Capabilities:
- **Page analysis** - Understand any webpage content
- **Knowledge integration** - Connect to your ML book collection
- **Notebook saving** - Save insights to your enhanced notebook
- **Real-time research** - Ask questions about anything

### Privacy & Control:
- **Local processing** - Your data stays on your machine
- **No external APIs** - Everything runs through your research agent
- **Full control** - You own your research assistant

## 🐛 Troubleshooting

### Extension Not Loading:
- Check that all files are in the `browser_extension/` directory
- Ensure `manifest.json` is valid
- Try reloading the extension

### Agent Connection Issues:
- Make sure your research agent is running locally
- Check that port 8000 is available
- Verify your `.env` file has the correct API key

### Sidebar Not Appearing:
- Check browser console for errors
- Ensure the page allows content scripts
- Try refreshing the page

## 🔄 Updates

To update the extension:
1. Make changes to the extension files
2. Go to `chrome://extensions/`
3. Click the refresh icon on your extension
4. The changes will be applied immediately

## 🎉 You're Ready!

Your Deep Research Agent is now **everywhere on the web** - just like Sider, but with your own powerful research capabilities!

**Next Steps:**
1. Start your research agent: `research julius`
2. Open any webpage
3. Click your extension icon
4. Start researching! 🧠 