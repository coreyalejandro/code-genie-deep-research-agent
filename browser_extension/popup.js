// Deep Research Agent Popup JavaScript
class ResearchAgentPopup {
  constructor() {
    this.initializeElements();
    this.bindEvents();
    this.loadRecentSearches();
    this.checkAgentStatus();
  }

  initializeElements() {
    this.openSidebarBtn = document.getElementById('openSidebar');
    this.analyzePageBtn = document.getElementById('analyzePage');
    this.saveToNotebookBtn = document.getElementById('saveToNotebook');
    this.researchQuery = document.getElementById('researchQuery');
    this.askAgentBtn = document.getElementById('askAgent');
    this.recentList = document.getElementById('recentList');
    this.statusIndicator = document.getElementById('statusIndicator');
  }

  bindEvents() {
    this.openSidebarBtn.addEventListener('click', () => this.openSidebar());
    this.analyzePageBtn.addEventListener('click', () => this.analyzeCurrentPage());
    this.saveToNotebookBtn.addEventListener('click', () => this.saveToNotebook());
    this.askAgentBtn.addEventListener('click', () => this.askAgent());
    this.researchQuery.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.askAgent();
      }
    });
  }

  async openSidebar() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: this.injectSidebar
      });
      window.close();
    } catch (error) {
      console.error('Error opening sidebar:', error);
      this.showError('Failed to open sidebar');
    }
  }

  injectSidebar() {
    // This function will be injected into the page
    if (document.getElementById('research-agent-sidebar')) {
      return; // Sidebar already exists
    }

    const sidebar = document.createElement('div');
    sidebar.id = 'research-agent-sidebar';
    sidebar.innerHTML = `
      <div class="sidebar-header">
        <h3>🧠 Deep Research Agent</h3>
        <button id="close-sidebar">×</button>
      </div>
      <div class="sidebar-content">
        <div class="chat-container">
          <div id="chat-messages"></div>
          <div class="input-container">
            <textarea id="chat-input" placeholder="Ask me anything about this page..."></textarea>
            <button id="send-message">Send</button>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(sidebar);
    
    // Add event listeners
    document.getElementById('close-sidebar').addEventListener('click', () => {
      sidebar.remove();
    });
    
    document.getElementById('send-message').addEventListener('click', () => {
      const input = document.getElementById('chat-input');
      const message = input.value.trim();
      if (message) {
        this.sendMessage(message);
        input.value = '';
      }
    });
  }

  async analyzeCurrentPage() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const pageContent = await this.extractPageContent(tab.id);
      
      this.researchQuery.value = `Analyze this page content and provide key insights: ${pageContent.substring(0, 500)}...`;
      this.askAgent();
    } catch (error) {
      console.error('Error analyzing page:', error);
      this.showError('Failed to analyze page');
    }
  }

  async extractPageContent(tabId) {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      function: () => {
        return {
          title: document.title,
          url: window.location.href,
          content: document.body.innerText.substring(0, 2000),
          headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent).join(', ')
        };
      }
    });
    
    return results[0].result;
  }

  async saveToNotebook() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const pageData = await this.extractPageContent(tab.id);
      
      // Save to local storage for now (can be enhanced to save to your notebook)
      const notebookEntry = {
        url: pageData.url,
        title: pageData.title,
        content: pageData.content,
        timestamp: new Date().toISOString(),
        type: 'webpage'
      };
      
      const existing = await this.getStorageData('notebook_entries') || [];
      existing.push(notebookEntry);
      await this.setStorageData('notebook_entries', existing);
      
      this.showSuccess('Saved to notebook!');
    } catch (error) {
      console.error('Error saving to notebook:', error);
      this.showError('Failed to save to notebook');
    }
  }

  async askAgent() {
    const query = this.researchQuery.value.trim();
    if (!query) {
      this.showError('Please enter a research question');
      return;
    }

    this.setStatus('thinking', 'Agent thinking...');
    this.askAgentBtn.disabled = true;
    this.askAgentBtn.textContent = 'Thinking...';

    try {
      // Get current page context
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const pageData = await this.extractPageContent(tab.id);
      
      // Prepare the research request
      const researchRequest = {
        query: query,
        context: {
          pageTitle: pageData.title,
          pageUrl: pageData.url,
          pageContent: pageData.content.substring(0, 1000)
        },
        timestamp: new Date().toISOString()
      };

      // Send to your research agent API
      const response = await this.sendToResearchAgent(researchRequest);
      
      // Save to recent searches
      this.saveRecentSearch(query, response);
      
      // Show response (in a real implementation, this would open the sidebar with the response)
      this.showResponse(response);
      
    } catch (error) {
      console.error('Error asking agent:', error);
      this.showError('Failed to get response from agent');
    } finally {
      this.setStatus('ready', 'Agent Ready');
      this.askAgentBtn.disabled = false;
      this.askAgentBtn.textContent = 'Ask Agent';
    }
  }

  async sendToResearchAgent(request) {
    // This would connect to your local research agent API
    // For now, we'll simulate a response
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          answer: `Based on your question "${request.query}", here's what I found in your research database and the current page context...`,
          sources: ['Your ML books', 'Current webpage'],
          confidence: 0.85
        });
      }, 2000);
    });
  }

  async loadRecentSearches() {
    try {
      const recent = await this.getStorageData('recent_searches') || [];
      this.recentList.innerHTML = '';
      
      recent.slice(0, 5).forEach(search => {
        const item = document.createElement('div');
        item.className = 'recent-item';
        item.textContent = search.query.substring(0, 50) + '...';
        item.addEventListener('click', () => {
          this.researchQuery.value = search.query;
        });
        this.recentList.appendChild(item);
      });
    } catch (error) {
      console.error('Error loading recent searches:', error);
    }
  }

  async saveRecentSearch(query, response) {
    try {
      const recent = await this.getStorageData('recent_searches') || [];
      const newSearch = {
        query: query,
        response: response,
        timestamp: new Date().toISOString()
      };
      
      // Add to beginning and keep only last 10
      recent.unshift(newSearch);
      const updated = recent.slice(0, 10);
      
      await this.setStorageData('recent_searches', updated);
      this.loadRecentSearches();
    } catch (error) {
      console.error('Error saving recent search:', error);
    }
  }

  async checkAgentStatus() {
    try {
      // Check if your local research agent is running
      const response = await fetch('http://localhost:8000/health', { 
        method: 'GET',
        mode: 'no-cors'
      });
      this.setStatus('ready', 'Agent Ready');
    } catch (error) {
      this.setStatus('error', 'Agent Offline');
    }
  }

  setStatus(type, message) {
    const dot = this.statusIndicator.querySelector('.dot');
    const text = this.statusIndicator.querySelector('span:last-child');
    
    dot.className = `dot ${type}`;
    text.textContent = message;
  }

  showResponse(response) {
    // In a real implementation, this would show the response in the sidebar
    console.log('Agent Response:', response);
    this.showSuccess('Response received! Check the sidebar.');
  }

  showSuccess(message) {
    // Simple success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: #4ade80;
      color: white;
      padding: 10px;
      border-radius: 5px;
      font-size: 12px;
      z-index: 10000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
  }

  showError(message) {
    // Simple error notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: #f87171;
      color: white;
      padding: 10px;
      border-radius: 5px;
      font-size: 12px;
      z-index: 10000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
  }

  async getStorageData(key) {
    return new Promise((resolve) => {
      chrome.storage.local.get([key], (result) => {
        resolve(result[key]);
      });
    });
  }

  async setStorageData(key, value) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [key]: value }, resolve);
    });
  }
}

// Initialize the popup when the page loads
document.addEventListener('DOMContentLoaded', () => {
  new ResearchAgentPopup();
}); 