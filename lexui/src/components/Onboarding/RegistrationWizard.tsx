/**
 * Registration Wizard Component
 * Multi-step user registration with demographics and ancestry
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, UserRegistration } from '../../services/api';
import { User, Globe, Heart, ChevronRight, ChevronLeft } from 'lucide-react';

interface RegistrationStep {
  title: string;
  description: string;
}

const REGISTRATION_STEPS: RegistrationStep[] = [
  { title: 'Account Setup', description: 'Basic account information' },
  { title: 'Demographics', description: 'Age, height, weight, sex' },
  { title: 'Ancestry & Background', description: 'Birthplace and family origins' },
  { title: 'Privacy Settings', description: 'Data sharing preferences' }
];

export const RegistrationWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [registrationData, setRegistrationData] = useState<Partial<UserRegistration>>({
    email: '',
    demographics: {
      age: 0,
      sex: 'other',
      height_cm: 0,
      weight_kg: 0,
      birthplace: '',
      parents_origin: ['', ''],
      self_ethnicity: ''
    },
    privacy_settings: {
      data_sharing: false,
      research_participation: false
    }
  });

  const navigate = useNavigate();

  const updateRegistrationData = (field: string, value: any) => {
    setRegistrationData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateDemographics = (field: string, value: any) => {
    setRegistrationData(prev => ({
      ...prev,
      demographics: {
        ...prev.demographics!,
        [field]: value
      }
    }));
  };

  const handleRegistration = async () => {
    setIsLoading(true);
    
    try {
      const result = await apiService.registerUser(registrationData as UserRegistration);
      
      if (result.user_id) {
        // Store user ID for the session
        localStorage.setItem('lexrag_user_id', result.user_id);
        
        // Navigate to data upload step
        navigate('/onboarding/upload');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < REGISTRATION_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleRegistration();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={registrationData.email}
                onChange={(e) => updateRegistrationData('email', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your.email@example.com"
                required
              />
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Age
                </label>
                <input
                  type="number"
                  value={registrationData.demographics?.age || ''}
                  onChange={(e) => updateDemographics('age', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="35"
                  min="0"
                  max="120"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sex
                </label>
                <select
                  value={registrationData.demographics?.sex}
                  onChange={(e) => updateDemographics('sex', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="other">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Height (cm)
                </label>
                <input
                  type="number"
                  value={registrationData.demographics?.height_cm || ''}
                  onChange={(e) => updateDemographics('height_cm', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="175"
                  min="50"
                  max="250"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  value={registrationData.demographics?.weight_kg || ''}
                  onChange={(e) => updateDemographics('weight_kg', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="70"
                  min="5"
                  max="300"
                />
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Where were you born?
              </label>
              <input
                type="text"
                value={registrationData.demographics?.birthplace || ''}
                onChange={(e) => updateDemographics('birthplace', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Sweden, Vietnam, Nigeria"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Where are your parents from?
              </label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={registrationData.demographics?.parents_origin[0] || ''}
                  onChange={(e) => {
                    const newOrigins = [...(registrationData.demographics?.parents_origin || ['', ''])];
                    newOrigins[0] = e.target.value;
                    updateDemographics('parents_origin', newOrigins);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Parent 1 origin"
                />
                <input
                  type="text"
                  value={registrationData.demographics?.parents_origin[1] || ''}
                  onChange={(e) => {
                    const newOrigins = [...(registrationData.demographics?.parents_origin || ['', ''])];
                    newOrigins[1] = e.target.value;
                    updateDemographics('parents_origin', newOrigins);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Parent 2 origin"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                How would you describe your ethnicity?
              </label>
              <input
                type="text"
                value={registrationData.demographics?.self_ethnicity || ''}
                onChange={(e) => updateDemographics('self_ethnicity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Swedish-Nigerian, Vietnamese, Italian"
              />
            </div>
            
            <div className="bg-blue-50 p-4 rounded-md">
              <p className="text-sm text-blue-800">
                <Globe className="inline w-4 h-4 mr-1" />
                This information helps us create your personalized genetic baseline using 
                population-specific data from our 4.4 billion record database.
              </p>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="data_sharing"
                  checked={registrationData.privacy_settings?.data_sharing || false}
                  onChange={(e) => updateRegistrationData('privacy_settings', {
                    ...registrationData.privacy_settings,
                    data_sharing: e.target.checked
                  })}
                  className="mr-3"
                />
                <label htmlFor="data_sharing" className="text-sm">
                  Allow anonymous data sharing for research (helps improve the platform)
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="research_participation"
                  checked={registrationData.privacy_settings?.research_participation || false}
                  onChange={(e) => updateRegistrationData('privacy_settings', {
                    ...registrationData.privacy_settings,
                    research_participation: e.target.checked
                  })}
                  className="mr-3"
                />
                <label htmlFor="research_participation" className="text-sm">
                  Participate in genomics research studies (optional)
                </label>
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-md">
              <p className="text-sm text-green-800">
                <Heart className="inline w-4 h-4 mr-1" />
                Your data is encrypted and secure. You can change these settings anytime.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 0:
        return registrationData.email && registrationData.email.includes('@');
      case 1:
        return registrationData.demographics?.age && 
               registrationData.demographics?.sex !== 'other' &&
               registrationData.demographics?.height_cm &&
               registrationData.demographics?.weight_kg;
      case 2:
        return registrationData.demographics?.birthplace &&
               registrationData.demographics?.self_ethnicity;
      case 3:
        return true; // Privacy settings are optional
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to LexRAG
          </h1>
          <p className="text-gray-600">
            Your Personalized Genomics Platform
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Step {currentStep + 1} of {REGISTRATION_STEPS.length}</span>
            <span>{Math.round(((currentStep + 1) / REGISTRATION_STEPS.length) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / REGISTRATION_STEPS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            {REGISTRATION_STEPS[currentStep].title}
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            {REGISTRATION_STEPS[currentStep].description}
          </p>
          
          {renderStep()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className={`flex items-center px-4 py-2 rounded-md ${
              currentStep === 0 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </button>

          <button
            onClick={nextStep}
            disabled={!isStepValid() || isLoading}
            className={`flex items-center px-4 py-2 rounded-md ${
              !isStepValid() || isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {isLoading ? (
              'Creating Account...'
            ) : currentStep === REGISTRATION_STEPS.length - 1 ? (
              <>
                Create Account
                <User className="w-4 h-4 ml-1" />
              </>
            ) : (
              <>
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </>
            )}
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Your data is encrypted and secure. We use ancestry information only 
            for population-specific genetic baselines, never for discrimination.
          </p>
        </div>
      </div>
    </div>
  );
};
