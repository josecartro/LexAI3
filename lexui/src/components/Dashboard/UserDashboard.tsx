/**
 * User Dashboard Component
 * Main dashboard showing user profile, digital twin status, and quick actions
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, UserProfile, DigitalTwin } from '../../services/api';
import { 
  User, Dna, Activity, MessageCircle, Settings, 
  TrendingUp, AlertCircle, CheckCircle, Upload 
} from 'lucide-react';

export const UserDashboard: React.FC = () => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const navigate = useNavigate();
  const userId = localStorage.getItem('lexrag_user_id');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      if (!userId) {
        navigate('/register');
        return;
      }

      const [profileData, twinData] = await Promise.all([
        apiService.getUserProfile(userId),
        apiService.getDigitalTwin(userId)
      ]);

      setUserProfile(profileData);
      setDigitalTwin(twinData);
    } catch (error) {
      console.error('Failed to load user data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getCompletenessColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getCompletenessGrade = (score: number) => {
    if (score >= 80) return 'A';
    if (score >= 60) return 'B';
    if (score >= 40) return 'C';
    return 'D';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
          <p className="text-gray-600">Loading your genomic profile...</p>
        </div>
      </div>
    );
  }

  if (!userProfile || !digitalTwin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <p className="text-gray-600">Failed to load user data</p>
          <button 
            onClick={loadUserData}
            className="mt-3 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const completenessScore = digitalTwin.completeness_score * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Your Genomic Dashboard</h1>
              <p className="text-gray-600">
                Welcome back! Your digital twin is {completenessScore.toFixed(1)}% complete.
              </p>
            </div>
            <button
              onClick={() => navigate('/chat')}
              className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat with AI
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Overview */}
          <div className="lg:col-span-2 space-y-6">
            {/* Digital Twin Status */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Digital Twin Status</h2>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getCompletenessColor(completenessScore)}`}>
                  Grade {getCompletenessGrade(completenessScore)}
                </div>
              </div>
              
              {/* Completeness Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Data Completeness</span>
                  <span>{completenessScore.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full transition-all duration-500 ${
                      completenessScore >= 80 ? 'bg-green-500' : 
                      completenessScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${completenessScore}%` }}
                  />
                </div>
              </div>

              {/* Data Sources */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center">
                  <Dna className="w-4 h-4 text-blue-500 mr-2" />
                  <span>DNA Data: {userProfile.data_summary.genomic_files > 0 ? 'Uploaded' : 'Not uploaded'}</span>
                </div>
                <div className="flex items-center">
                  <Activity className="w-4 h-4 text-green-500 mr-2" />
                  <span>Devices: {userProfile.data_summary.devices_connected} connected</span>
                </div>
                <div className="flex items-center">
                  <User className="w-4 h-4 text-purple-500 mr-2" />
                  <span>Questionnaire: {userProfile.data_summary.questionnaire_responses} responses</span>
                </div>
                <div className="flex items-center">
                  <TrendingUp className="w-4 h-4 text-orange-500 mr-2" />
                  <span>Quality: {(userProfile.data_summary.avg_quality_score * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Genetic Summary */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Genetic Profile Summary</h2>
              
              {userProfile.data_summary.genomic_files > 0 ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Total Variants:</span>
                    <span className="font-medium">{userProfile.data_summary.total_variants.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Data Quality:</span>
                    <span className="font-medium">{(userProfile.data_summary.avg_quality_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Files Uploaded:</span>
                    <span className="font-medium">{userProfile.data_summary.genomic_files}</span>
                  </div>
                  
                  <div className="mt-4 p-3 bg-green-50 rounded-md">
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      <span className="text-sm text-green-800">
                        Your genetic data is being used for personalized analysis
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <h3 className="font-medium text-gray-900 mb-2">No Genetic Data Yet</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Upload your DNA data for personalized genomic analysis
                  </p>
                  <button
                    onClick={() => navigate('/upload-dna')}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                  >
                    Upload DNA Data
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/chat')}
                  className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  <MessageCircle className="w-4 h-4 mr-3" />
                  Chat with DNA Expert
                </button>
                
                <button
                  onClick={() => navigate('/upload-dna')}
                  className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  <Upload className="w-4 h-4 mr-3" />
                  Upload DNA Data
                </button>
                
                <button
                  onClick={() => navigate('/questionnaire')}
                  className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  <User className="w-4 h-4 mr-3" />
                  Complete Questionnaire
                </button>
                
                <button
                  onClick={() => navigate('/settings')}
                  className="w-full flex items-center px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  <Settings className="w-4 h-4 mr-3" />
                  Privacy Settings
                </button>
              </div>
            </div>

            {/* Data Sources */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h2>
              <div className="space-y-3 text-sm">
                {Object.entries(digitalTwin.data_sources).map(([category, source]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-gray-600 capitalize">{category.replace('_', ' ')}:</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      source === 'user_specific' ? 'bg-green-100 text-green-800' :
                      source === 'population_matched' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {source === 'user_specific' ? 'Your Data' :
                       source === 'population_matched' ? 'Population' :
                       'Reference'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Status</h2>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Genomic Database:</span>
                  <span className="text-green-600">4.4B records</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">AI Model:</span>
                  <span className="text-green-600">DNA Expert</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Digital Twin:</span>
                  <span className="text-green-600">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
