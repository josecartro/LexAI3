/**
 * Chat Interface Component
 * Main AI chat interface with DNA Expert model integration
 */

import React, { useState, useEffect, useRef } from 'react';
import { apiService, ChatResponse } from '../../services/api';
import { Send, Bot, User, Info, TrendingUp, AlertTriangle } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  confidence_level?: 'high' | 'medium' | 'low';
  data_sources?: Record<string, string>;
  recommendations?: string[];
  timestamp: Date;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const [userCompleteness, setUserCompleteness] = useState(0);
  const [aiProgress, setAiProgress] = useState<string>('');
  const [abortStream, setAbortStream] = useState<(() => void) | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const userId = localStorage.getItem('lexrag_user_id');

  useEffect(() => {
    // Initialize conversation and load user context
    initializeChat();
    loadUserContext();
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initializeChat = async () => {
    try {
      if (!userId) return;
      
      const newConversation = await apiService.startNewConversation(userId);
      setConversationId(newConversation.conversation_id);
      
      // Add welcome message based on user context
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'ai',
        content: `Welcome to your personalized genomics assistant! I have access to 4.4 billion genomic records and your digital twin. ${newConversation.user_context_summary.has_genomic_data ? 'I can see you have genetic data uploaded.' : 'I can help you understand genetics even without your personal data.'} What would you like to know?`,
        confidence_level: newConversation.user_context_summary.confidence_level,
        timestamp: new Date()
      };
      
      setMessages([welcomeMessage]);
      setUserCompleteness(parseFloat(newConversation.user_context_summary.data_completeness) || 0);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const loadUserContext = async () => {
    try {
      if (!userId) return;
      
      const twinData = await apiService.getDigitalTwin(userId);
      setUserCompleteness(twinData.completeness_score * 100);
    } catch (error) {
      console.error('Failed to load user context:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !userId || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = currentMessage;
    setCurrentMessage('');
    setIsLoading(true);
    setAiProgress('Connecting to AI...');

    try {
      // Use streaming API for real-time progress updates
      const abort = apiService.chatWithAIStream(
        userId,
        {
          message: messageToSend,
          conversation_id: conversationId
        },
        // Progress callback
        (update) => {
          console.log('Progress update:', update);
          
          // Update progress message based on status
          switch (update.status) {
            case 'starting':
              setAiProgress('🧬 Initializing AI analysis...');
              break;
            case 'loading_context':
              setAiProgress('📊 Loading your digital twin...');
              break;
            case 'thinking':
              setAiProgress(`🤔 AI reasoning (step ${update.data?.iteration || 1}/${update.data?.max_iterations || 12})...`);
              break;
            case 'querying_model':
              setAiProgress('🧠 Consulting DNA Expert AI...');
              break;
            case 'executing_tool':
              setAiProgress(`🔧 Accessing genomic databases: ${update.message}`);
              break;
            case 'tool_executing':
              setAiProgress(`📡 Gathering data: ${update.data?.tool || 'tool'}...`);
              break;
            case 'tool_complete':
              setAiProgress(`✅ Data retrieved from ${update.data?.tool || 'database'}`);
              break;
            case 'finalizing':
              setAiProgress('✍️ Formulating response...');
              break;
            case 'complete':
              setAiProgress('✅ Complete!');
              break;
            default:
              if (update.message) {
                setAiProgress(update.message);
              }
          }
        },
        // Complete callback
        (result) => {
          setIsLoading(false);
          setAiProgress('');
          setAbortStream(null);
          
          const aiMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: result.response,
            confidence_level: result.confidence_level,
            data_sources: result.data_sources,
            recommendations: result.recommendations,
            timestamp: new Date()
          };

          setMessages(prev => [...prev, aiMessage]);
        },
        // Error callback
        (error) => {
          setIsLoading(false);
          setAiProgress('');
          setAbortStream(null);
          
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: `❌ Error: ${error}. Please ensure LM Studio is running with the DNA Expert model loaded on port 1234.`,
            confidence_level: 'low',
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, errorMessage]);
        }
      );
      
      setAbortStream(() => abort);

    } catch (error) {
      setIsLoading(false);
      setAiProgress('');
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'I apologize, but I encountered an error processing your request. Please try again or rephrase your question.',
        confidence_level: 'low',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getConfidenceColor = (level?: string) => {
    switch (level) {
      case 'high': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getConfidenceIcon = (level?: string) => {
    switch (level) {
      case 'high': return <TrendingUp className="w-4 h-4" />;
      case 'medium': return <Info className="w-4 h-4" />;
      case 'low': return <AlertTriangle className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const suggestedQuestions = [
    "What do my genetic variants mean for my health?",
    "What medications should I avoid based on my genetics?",
    "What is my risk for common diseases?",
    "How do my genes affect my response to exercise and diet?",
    "Should my family members get genetic testing?"
  ];

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Bot className="w-6 h-6 text-blue-500 mr-2" />
            <h1 className="text-lg font-semibold text-gray-900">
              DNA Expert Assistant
            </h1>
          </div>
          <div className="text-sm text-gray-500">
            Data completeness: {userCompleteness.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-3xl ${message.type === 'user' ? 'order-2' : ''}`}>
              {/* Message Bubble */}
              <div
                className={`px-4 py-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                <div className="flex items-start">
                  {message.type === 'ai' && (
                    <Bot className="w-5 h-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    
                    {/* Confidence Indicator for AI messages */}
                    {message.type === 'ai' && message.confidence_level && (
                      <div className={`inline-flex items-center mt-2 px-2 py-1 rounded-full text-xs ${getConfidenceColor(message.confidence_level)}`}>
                        {getConfidenceIcon(message.confidence_level)}
                        <span className="ml-1 capitalize">{message.confidence_level} Confidence</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Data Sources */}
                {message.type === 'ai' && message.data_sources && Object.keys(message.data_sources).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-2">Data Sources:</p>
                    <div className="space-y-1">
                      {Object.entries(message.data_sources).map(([category, source]) => (
                        <div key={category} className="text-xs">
                          <span className="font-medium">{category}:</span> 
                          <span className="text-gray-600 ml-1">{source}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {message.type === 'ai' && message.recommendations && message.recommendations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-2">Recommendations:</p>
                    <ul className="space-y-1">
                      {message.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-xs text-gray-600">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <p className="text-xs text-gray-400 mt-1 px-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
            
            {/* User Avatar */}
            {message.type === 'user' && (
              <User className="w-8 h-8 text-gray-400 ml-2 mt-1 order-1" />
            )}
          </div>
        ))}
        
        {/* Loading Indicator with Progress */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-blue-200 rounded-lg px-4 py-3 shadow-sm">
              <div className="flex items-center">
                <Bot className="w-5 h-5 text-blue-500 mr-2 animate-bounce" />
                <div className="flex space-x-1 mr-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '150ms'}} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '300ms'}} />
                </div>
                <span className="ml-2 text-sm text-gray-700 font-medium">
                  {aiProgress || 'Connecting to AI...'}
                </span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (when no messages) */}
      {messages.length <= 1 && !isLoading && (
        <div className="px-4 pb-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="font-medium text-gray-900 mb-3">Suggested Questions:</h3>
            <div className="space-y-2">
              {suggestedQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentMessage(question)}
                  className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md border border-gray-200"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your genetics, health risks, medications, or anything genomics-related..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading}
            className={`px-4 py-2 rounded-md ${
              !currentMessage.trim() || isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};
