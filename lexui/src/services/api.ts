/**
 * API Service Layer for LexRAG Platform
 * Handles all communication with LexRAG APIs
 */

import axios from 'axios';

// API Base URLs
const API_BASE = {
  users: 'http://127.0.0.1:8007',
  digitalTwin: 'http://127.0.0.1:8008', 
  aiGateway: 'http://127.0.0.1:8009',
  genomics: 'http://127.0.0.1:8001',
  anatomics: 'http://127.0.0.1:8002',
  literature: 'http://127.0.0.1:8003'
};

// Types
export interface UserRegistration {
  email: string;
  demographics: {
    age: number;
    sex: 'male' | 'female' | 'other';
    height_cm: number;
    weight_kg: number;
    birthplace: string;
    parents_origin: string[];
    self_ethnicity: string;
  };
  privacy_settings?: {
    data_sharing: boolean;
    research_participation: boolean;
  };
}

export interface UserProfile {
  user_id: string;
  email: string;
  demographics: any;
  medical_history: any;
  data_summary: {
    genomic_files: number;
    total_variants: number;
    avg_quality_score: number;
    devices_connected: number;
    questionnaire_responses: number;
  };
}

export interface DigitalTwin {
  user_id: string;
  twin_data: any;
  data_sources: Record<string, string>;
  confidence_scores: Record<string, number>;
  completeness_score: number;
  twin_status: string;
}

export interface ChatMessage {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  ai_response: {
    response: string;
    confidence_level: 'high' | 'medium' | 'low';
    data_sources: Record<string, string>;
    recommendations: string[];
  };
}

// API Service Class
class APIService {
  // User Management APIs
  async registerUser(userData: UserRegistration): Promise<{ user_id: string; status: string }> {
    const response = await axios.post(`${API_BASE.users}/users/register`, userData);
    return response.data;
  }

  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await axios.get(`${API_BASE.users}/users/${userId}/profile`);
    return response.data;
  }

  async uploadDNA(userId: string, file: File, fileType: string = 'auto'): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(
      `${API_BASE.users}/users/${userId}/upload-dna?file_type=${fileType}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getUserDataStatus(userId: string): Promise<any> {
    const response = await axios.get(`${API_BASE.users}/users/${userId}/data-status`);
    return response.data;
  }

  async getAdaptiveQuestionnaire(userId: string): Promise<any> {
    const response = await axios.get(`${API_BASE.users}/users/${userId}/questionnaire`);
    return response.data;
  }

  async submitQuestionnaireResponses(userId: string, responses: any[]): Promise<any> {
    const response = await axios.post(`${API_BASE.users}/users/${userId}/questionnaire`, responses);
    return response.data;
  }

  // Digital Twin APIs
  async getDigitalTwin(userId: string): Promise<DigitalTwin> {
    const response = await axios.get(`${API_BASE.digitalTwin}/twin/${userId}/model`);
    return response.data;
  }

  async getAdamReference(): Promise<any> {
    const response = await axios.get(`${API_BASE.digitalTwin}/twin/reference/adam`);
    return response.data;
  }

  async getEveReference(): Promise<any> {
    const response = await axios.get(`${API_BASE.digitalTwin}/twin/reference/eve`);
    return response.data;
  }

  async getTwinCompleteness(userId: string): Promise<any> {
    const response = await axios.get(`${API_BASE.digitalTwin}/twin/${userId}/completeness`);
    return response.data;
  }

  async getTwinConfidence(userId: string): Promise<any> {
    const response = await axios.get(`${API_BASE.digitalTwin}/twin/${userId}/confidence`);
    return response.data;
  }

  // AI Chat APIs
  async chatWithAI(userId: string, message: ChatMessage): Promise<ChatResponse> {
    const response = await axios.post(`${API_BASE.aiGateway}/chat/${userId}`, message);
    return response.data;
  }

  // Streaming chat with real-time progress updates
  chatWithAIStream(
    userId: string, 
    message: ChatMessage,
    onProgress: (update: any) => void,
    onComplete: (result: any) => void,
    onError: (error: string) => void
  ): () => void {
    const abortController = new AbortController();
    
    console.log('[SSE] Starting stream for user:', userId, 'message:', message.message);
    
    fetch(`${API_BASE.aiGateway}/chat/${userId}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message),
      signal: abortController.signal
    })
    .then(async (response) => {
      console.log('[SSE] Response received, status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body');
      }
      
      console.log('[SSE] Starting to read stream...');
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('[SSE] Stream complete');
          break;
        }
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              console.log('[SSE] Received update:', data);
              
              if (data.status === 'done') {
                console.log('[SSE] Analysis complete, result:', data.result);
                onComplete(data.result);
              } else if (data.status === 'error') {
                console.log('[SSE] Error received:', data);
                onError(data.error || data.message || 'Unknown error');
              } else {
                console.log('[SSE] Progress update:', data.status, data.message);
                onProgress(data);
              }
            } catch (e) {
              console.error('[SSE] Failed to parse SSE data:', e, 'Line:', line);
            }
          }
        }
      }
    })
    .catch((error) => {
      console.error('[SSE] Stream error:', error);
      if (error.name !== 'AbortError') {
        onError(error.message);
      }
    });
    
    // Return abort function
    return () => abortController.abort();
  }

  async getChatHistory(userId: string, conversationId?: string): Promise<any> {
    const url = conversationId 
      ? `${API_BASE.aiGateway}/chat/${userId}/history?conversation_id=${conversationId}`
      : `${API_BASE.aiGateway}/chat/${userId}/history`;
    
    const response = await axios.get(url);
    return response.data;
  }

  async startNewConversation(userId: string): Promise<any> {
    const response = await axios.post(`${API_BASE.aiGateway}/chat/${userId}/new-conversation`);
    return response.data;
  }

  // Genomics Analysis APIs
  async analyzeGene(geneSymbol: string): Promise<any> {
    const response = await axios.get(`${API_BASE.genomics}/analyze/gene/${geneSymbol}`);
    return response.data;
  }

  async analyzeVariant(variantId: string): Promise<any> {
    const response = await axios.get(`${API_BASE.genomics}/analyze/variant/${variantId}`);
    return response.data;
  }

  // Health Check APIs
  async checkSystemHealth(): Promise<Record<string, any>> {
    const healthChecks = await Promise.allSettled([
      axios.get(`${API_BASE.users}/health`),
      axios.get(`${API_BASE.digitalTwin}/health`),
      axios.get(`${API_BASE.aiGateway}/health`),
      axios.get(`${API_BASE.genomics}/health`),
      axios.get(`${API_BASE.anatomics}/health`),
      axios.get(`${API_BASE.literature}/health`)
    ]);

    return {
      users: healthChecks[0].status === 'fulfilled' ? healthChecks[0].value.data : { status: 'error' },
      digitalTwin: healthChecks[1].status === 'fulfilled' ? healthChecks[1].value.data : { status: 'error' },
      aiGateway: healthChecks[2].status === 'fulfilled' ? healthChecks[2].value.data : { status: 'error' },
      genomics: healthChecks[3].status === 'fulfilled' ? healthChecks[3].value.data : { status: 'error' },
      anatomics: healthChecks[4].status === 'fulfilled' ? healthChecks[4].value.data : { status: 'error' },
      literature: healthChecks[5].status === 'fulfilled' ? healthChecks[5].value.data : { status: 'error' }
    };
  }
}

// Export singleton instance
export const apiService = new APIService();

