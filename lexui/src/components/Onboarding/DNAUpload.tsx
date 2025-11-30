/**
 * DNA Upload Component
 * Handles DNA file upload with progress tracking and format detection
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { Upload, FileText, CheckCircle, AlertCircle, Dna } from 'lucide-react';

interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  message: string;
}

export const DNAUpload: React.FC = () => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    status: 'idle',
    progress: 0,
    message: ''
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<string>('auto');
  
  const navigate = useNavigate();
  const userId = localStorage.getItem('lexrag_user_id');

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      // Auto-detect file type based on name
      const fileName = file.name.toLowerCase();
      if (fileName.includes('23andme')) {
        setFileType('23andme');
      } else if (fileName.includes('ancestry')) {
        setFileType('ancestry');
      } else if (fileName.includes('myheritage')) {
        setFileType('myheritage');
      } else if (fileName.endsWith('.vcf') || fileName.endsWith('.vcf.gz')) {
        setFileType('vcf');
      } else {
        setFileType('auto');
      }
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedFile || !userId) return;

    setUploadStatus({
      status: 'uploading',
      progress: 0,
      message: 'Uploading DNA file...'
    });

    try {
      // Upload file
      const uploadResult = await apiService.uploadDNA(userId, selectedFile, fileType);
      
      if (uploadResult.upload_status === 'success') {
        setUploadStatus({
          status: 'processing',
          progress: 50,
          message: `Processing ${uploadResult.processing_results.variants_found.toLocaleString()} variants...`
        });

        // Poll for processing completion
        pollProcessingStatus();
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setUploadStatus({
        status: 'error',
        progress: 0,
        message: 'Upload failed. Please check file format and try again.'
      });
    }
  };

  const pollProcessingStatus = async () => {
    const pollInterval = setInterval(async () => {
      try {
        if (!userId) return;
        
        const statusData = await apiService.getUserDataStatus(userId);
        
        if (statusData.status.dna_uploaded) {
          setUploadStatus({
            status: 'complete',
            progress: 100,
            message: `Complete! ${statusData.data_summary.total_variants.toLocaleString()} variants processed`
          });
          
          clearInterval(pollInterval);
          
          // Auto-navigate to questionnaire after 2 seconds
          setTimeout(() => {
            navigate('/onboarding/questionnaire');
          }, 2000);
        } else {
          // Update progress
          setUploadStatus(prev => ({
            ...prev,
            progress: Math.min(prev.progress + 10, 90),
            message: 'Analyzing genetic variants...'
          }));
        }
      } catch (error) {
        clearInterval(pollInterval);
        setUploadStatus({
          status: 'error',
          progress: 0,
          message: 'Processing failed. Please try again.'
        });
      }
    }, 3000);
  };

  const skipUpload = () => {
    navigate('/onboarding/questionnaire');
  };

  const getFileTypeDescription = (type: string) => {
    const descriptions: Record<string, string> = {
      '23andme': '23andMe raw data files (~25MB, 600K+ variants)',
      'ancestry': 'AncestryDNA raw data files (~15MB, 700K+ variants)', 
      'myheritage': 'MyHeritage raw data files (~20MB, 750K+ variants)',
      'vcf': 'VCF format files (variable size, research-grade)',
      'auto': 'Auto-detect format from file content'
    };
    return descriptions[type] || descriptions['auto'];
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-lg w-full bg-white rounded-lg shadow-lg p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <Dna className="w-12 h-12 text-blue-500 mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Upload Your DNA Data
          </h1>
          <p className="text-gray-600">
            Get personalized insights from your genetic information
          </p>
        </div>

        {/* Upload Area */}
        {uploadStatus.status === 'idle' && (
          <div className="space-y-6">
            {/* File Input */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
              
              <input
                type="file"
                id="dna-file"
                accept=".txt,.csv,.vcf,.gz,.zip"
                onChange={handleFileSelect}
                className="hidden"
              />
              
              <label
                htmlFor="dna-file"
                className="cursor-pointer text-blue-500 hover:text-blue-600 font-medium"
              >
                Choose DNA file
              </label>
              
              <p className="text-sm text-gray-500 mt-2">
                Supports 23andMe, AncestryDNA, MyHeritage, VCF formats
              </p>
            </div>

            {/* Selected File */}
            {selectedFile && (
              <div className="bg-blue-50 p-4 rounded-md">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-blue-500 mr-3" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-600">
                      {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
                    </p>
                  </div>
                </div>
                
                {/* File Type Selection */}
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    File Type:
                  </label>
                  <select
                    value={fileType}
                    onChange={(e) => setFileType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="auto">Auto-detect</option>
                    <option value="23andme">23andMe</option>
                    <option value="ancestry">AncestryDNA</option>
                    <option value="myheritage">MyHeritage</option>
                    <option value="vcf">VCF Format</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {getFileTypeDescription(fileType)}
                  </p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={skipUpload}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Skip for Now
              </button>
              <button
                onClick={handleUpload}
                disabled={!selectedFile}
                className={`flex-1 px-4 py-2 rounded-md ${
                  selectedFile 
                    ? 'bg-blue-500 text-white hover:bg-blue-600' 
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Upload & Process
              </button>
            </div>
          </div>
        )}

        {/* Processing Status */}
        {(uploadStatus.status === 'uploading' || uploadStatus.status === 'processing') && (
          <div className="space-y-4">
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
              <h3 className="font-medium text-gray-900">{uploadStatus.message}</h3>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${uploadStatus.progress}%` }}
              />
            </div>
            
            <p className="text-sm text-gray-600 text-center">
              This may take 2-5 minutes depending on file size
            </p>
          </div>
        )}

        {/* Complete Status */}
        {uploadStatus.status === 'complete' && (
          <div className="text-center space-y-4">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
            <div>
              <h3 className="font-medium text-gray-900 mb-1">Upload Complete!</h3>
              <p className="text-sm text-gray-600">{uploadStatus.message}</p>
            </div>
            <p className="text-xs text-gray-500">
              Redirecting to questionnaire...
            </p>
          </div>
        )}

        {/* Error Status */}
        {uploadStatus.status === 'error' && (
          <div className="text-center space-y-4">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
            <div>
              <h3 className="font-medium text-gray-900 mb-1">Upload Failed</h3>
              <p className="text-sm text-gray-600">{uploadStatus.message}</p>
            </div>
            <button
              onClick={() => setUploadStatus({ status: 'idle', progress: 0, message: '' })}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Supported Formats Info */}
        {uploadStatus.status === 'idle' && (
          <div className="mt-6 bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium text-gray-900 mb-2">Supported Formats:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• 23andMe raw data (most common)</li>
              <li>• AncestryDNA raw data</li>
              <li>• MyHeritage raw data</li>
              <li>• VCF files (whole genome/exome)</li>
              <li>• Generic CSV formats</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
