import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';
import { marked } from 'marked';

// Configure marked for safe HTML rendering
marked.setOptions({
  breaks: true,
  gfm: true
});

// User ID for demo purposes - in a real app this would come from auth
const DEMO_USER_ID = "user_12345";

function App() {
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiProgress, setAiProgress] = useState('');
  const [systemHealth, setSystemHealth] = useState<Record<string, any> | null>(null);
  const [messages, setMessages] = useState<{
    id: string;
    type: string;
    content: string;
    confidence?: string;
    dataSources?: Record<string, string>;
  }[]>([
    {
      id: '1',
      type: 'ai',
      content: '🧬 Welcome to LexRAG! I\'m your DNA Expert assistant. I have access to the complete LexRAG platform including your digital twin and 4.4 billion genomic records. How can I help you today?'
    }
  ]);

  const conversations = [
    { id: '1', title: 'Current Session', lastMessage: 'Active conversation' },
  ];

  // Parse markdown to HTML and strip "system" prefix
  const parseMarkdown = (text: string): string => {
    // Strip "system" prefix that LM Studio sometimes adds
    text = text.replace(/^system\s*\n+/, '');
    
    // Parse markdown to HTML
    const html = marked.parse(text) as string;
    
    return html;
  };

  // Check system health on load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiService.checkSystemHealth();
        setSystemHealth(health);
        console.log("System Health:", health);
      } catch (e) {
        console.error("Health check failed:", e);
      }
    };
    checkHealth();
  }, []);

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = currentMessage;
    setCurrentMessage('');
    setIsLoading(true);
    setAiProgress('Connecting to AI...');

    // Add loading indicator with progress
    const loadingId = 'loading-' + Date.now();
    setMessages(prev => [...prev, {
      id: loadingId,
      type: 'ai',
      content: 'Connecting to AI...'
    }]);

    try {
      // Use STREAMING API with real-time progress
      console.log("[SSE] Starting stream for message:", messageToSend);
      
      apiService.chatWithAIStream(
        DEMO_USER_ID,
        { message: messageToSend },
        // Progress callback
        (update) => {
          console.log('[SSE] Progress update:', update);
          
          let progressText = '';
          switch (update.status) {
            case 'starting':
              progressText = '🧬 Initializing AI analysis...';
              break;
            case 'loading_context':
              progressText = '📊 Loading your digital twin...';
              break;
            case 'thinking':
              progressText = `🤔 AI reasoning (step ${update.data?.iteration || 1}/${update.data?.max_iterations || 12})...`;
              break;
            case 'querying_model':
              progressText = '🧠 Consulting DNA Expert AI...';
              break;
            case 'executing_tool':
              progressText = `🔧 Accessing genomic databases: ${update.message}`;
              break;
            case 'tool_executing':
              progressText = `📡 Gathering data: ${update.data?.tool || 'tool'}...`;
              break;
            case 'tool_complete':
              progressText = `✅ Data retrieved from ${update.data?.tool || 'database'}`;
              break;
            case 'finalizing':
              progressText = '✍️ Formulating response...';
              break;
            case 'complete':
              progressText = '✅ Complete!';
              break;
            default:
              progressText = update.message || 'Processing...';
          }
          
          setAiProgress(progressText);
          
          // Update loading message with progress
          setMessages(prev => prev.map(m => 
            m.id === loadingId ? { ...m, content: progressText } : m
          ));
        },
        // Complete callback
        (result) => {
          console.log('[SSE] Analysis complete:', result);
          setIsLoading(false);
          setAiProgress('');
          
          // Remove loading message
          setMessages(prev => prev.filter(m => m.id !== loadingId));
          
          const aiMessage = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: result.response,
            confidence: result.confidence_level,
            dataSources: result.data_sources
          };
          
          setMessages(prev => [...prev, aiMessage]);
        },
        // Error callback
        (error) => {
          console.error('[SSE] Stream error:', error);
          setIsLoading(false);
          setAiProgress('');
          
          setMessages(prev => prev.filter(m => m.id !== loadingId));
          
          const errorMessage = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: `❌ Error: ${error}. Please ensure LM Studio is running with the DNA Expert model loaded on port 1234.`
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      );

    } catch (error) {
      console.error("Chat error:", error);
      setIsLoading(false);
      setAiProgress('');
      setMessages(prev => prev.filter(m => m.id !== loadingId));
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `Error: Unable to reach the AI Gateway (Port 8009). Please ensure 'start_all_apis.bat' is running.`
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* Left Column - Conversation List */}
      <div style={{ 
        width: '250px', 
        backgroundColor: '#1f2937', 
        color: 'white', 
        display: 'flex', 
        flexDirection: 'column' 
      }}>
        {/* Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #374151' }}>
          <h1 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>LexRAG</h1>
          <p style={{ fontSize: '14px', color: '#9ca3af', margin: '4px 0 0 0' }}>DNA Expert Assistant</p>
        </div>
        
        {/* New Chat Button */}
        <div style={{ padding: '12px' }}>
          <button style={{
            width: '100%',
            padding: '8px 12px',
            backgroundColor: '#374151',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer'
          }}>
            + New Chat
          </button>
        </div>
        
        {/* Conversation List */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {conversations.map((conv) => (
            <div
              key={conv.id}
              style={{
                padding: '12px',
                cursor: 'pointer',
                borderLeft: conv.id === '1' ? '2px solid #3b82f6' : '2px solid transparent',
                backgroundColor: conv.id === '1' ? '#374151' : 'transparent'
              }}
            >
              <p style={{ fontSize: '14px', fontWeight: '500', margin: 0, marginBottom: '4px' }}>
                {conv.title}
              </p>
              <p style={{ fontSize: '12px', color: '#9ca3af', margin: 0 }}>
                {conv.lastMessage}
              </p>
            </div>
          ))}
        </div>
        
        {/* User Profile */}
        <div style={{ padding: '12px', borderTop: '1px solid #374151' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              width: '32px', 
              height: '32px', 
              backgroundColor: '#6b7280', 
              borderRadius: '50%', 
              marginRight: '12px' 
            }} />
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '14px', fontWeight: '500', margin: 0 }}>Demo User</p>
              <p style={{ fontSize: '12px', color: '#9ca3af', margin: 0 }}>ID: {DEMO_USER_ID}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Middle Column - Chat Interface */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: 'white' }}>
        {/* Chat Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', margin: 0, marginBottom: '4px' }}>
            DNA Expert Chat
          </h2>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            Powered by LexRAG Gateway (Port 8009) + Qwen3-14B
          </p>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: 'flex',
                justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: '16px'
              }}
            >
              <div
                style={{
                  maxWidth: '70%',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  backgroundColor: message.type === 'user' ? '#3b82f6' : '#f3f4f6',
                  color: message.type === 'user' ? 'white' : '#1f2937'
                }}
              >
                {message.type === 'user' ? (
                  <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                    {message.content}
                  </p>
                ) : (
                  <div 
                    className="prose prose-sm max-w-none"
                    style={{ 
                      fontSize: '14px', 
                      lineHeight: '1.5',
                      color: '#1f2937'
                    }}
                    dangerouslySetInnerHTML={{ __html: parseMarkdown(message.content) }}
                  />
                )}
                
                {/* Confidence and Data Sources for AI messages */}
                {message.type === 'ai' && (message.confidence || message.dataSources) && (
                  <div style={{ 
                    marginTop: '8px', 
                    paddingTop: '8px', 
                    borderTop: '1px solid #e5e7eb',
                    fontSize: '12px'
                  }}>
                    {message.confidence && (
                      <div style={{ 
                        display: 'inline-block',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        backgroundColor: message.confidence === 'high' ? '#dcfce7' : 
                                       message.confidence === 'medium' ? '#fef3c7' : '#fee2e2',
                        color: message.confidence === 'high' ? '#166534' : 
                               message.confidence === 'medium' ? '#92400e' : '#991b1b',
                        marginBottom: '4px'
                      }}>
                        {message.confidence.toUpperCase()} CONFIDENCE
                      </div>
                    )}
                    
                    {message.dataSources && Object.keys(message.dataSources).length > 0 && (
                      <div style={{ marginTop: '4px' }}>
                        <strong>Data Sources:</strong>
                        {Object.entries(message.dataSources).map(([key, value]) => (
                          <div key={key} style={{ marginLeft: '8px', color: '#6b7280' }}>
                            • {key}: {value}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Message Input */}
        <div style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input
              type="text"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me about your genetics, health risks, medications..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                outline: 'none'
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!currentMessage.trim() || isLoading}
              style={{
                padding: '8px 16px',
                backgroundColor: !currentMessage.trim() || isLoading ? '#f3f4f6' : '#3b82f6',
                color: !currentMessage.trim() || isLoading ? '#9ca3af' : 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: !currentMessage.trim() || isLoading ? 'not-allowed' : 'pointer'
              }}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>

      {/* Right Column - System Status */}
      <div style={{ 
        width: '250px', 
        backgroundColor: 'white', 
        borderLeft: '1px solid #e5e7eb', 
        padding: '16px' 
      }}>
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: '500', margin: '0 0 8px 0' }}>
            System Status
          </h3>
          
          {!systemHealth ? (
            <p style={{ fontSize: '12px', color: '#6b7280' }}>Checking API health...</p>
          ) : (
            <div style={{ fontSize: '12px' }}>
              {Object.entries(systemHealth).map(([service, status]) => (
                <div key={service} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  marginBottom: '8px',
                  alignItems: 'center'
                }}>
                  <span style={{ textTransform: 'capitalize' }}>{service}:</span>
                  <span style={{ 
                    color: status.status === 'healthy' ? '#10b981' : '#ef4444',
                    fontWeight: '500'
                  }}>
                    {status.status === 'healthy' ? 'Online' : 'Offline'}
                  </span>
          </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
