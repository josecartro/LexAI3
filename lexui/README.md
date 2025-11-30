# LexUI - Frontend for LexRAG Platform

## Overview
React + TypeScript frontend for the LexRAG personalized genomics platform. Provides user registration, DNA upload, digital twin visualization, and AI chat interface.

## Features
- **User Registration Wizard** - Multi-step onboarding with ancestry collection
- **DNA File Upload** - Support for 23andMe, AncestryDNA, VCF formats with progress tracking
- **AI Chat Interface** - Conversational interface with DNA Expert model
- **Digital Twin Dashboard** - Visualization of user's genetic baseline and data completeness
- **Data Source Transparency** - Clear indication of data confidence levels
- **Responsive Design** - Works on desktop and mobile devices

## Architecture
```
LexUI (Frontend)
├── Registration Wizard → LexAPI_Users (8007)
├── DNA Upload → LexAPI_Users (8007) 
├── Digital Twin Viz → LexAPI_DigitalTwin (8008)
├── AI Chat → LexAPI_AIGateway (8009)
└── Data Dashboard → Multiple APIs
```

## User Journey
1. **Registration** - Demographics + ancestry → Digital twin created with population baselines
2. **DNA Upload** - File processing → Twin updated with user genetics → Confidence jumps to 85%+
3. **Smart Questionnaire** - Adaptive questions based on DNA findings → Further refinement
4. **AI Chat** - Comprehensive genomic analysis with 4.4B record access → Personalized insights

## Technology Stack
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for responsive styling
- **Axios** for API communication
- **React Router** for navigation
- **Lucide React** for icons

## Development

### Setup
```bash
npm install
npm run dev
```

### Build
```bash
npm run build
npm run preview
```

## API Integration
Connects to all LexRAG APIs:
- **LexAPI_Users (8007)** - User management and DNA processing
- **LexAPI_DigitalTwin (8008)** - Digital twin modeling with Adam/Eve baselines
- **LexAPI_AIGateway (8009)** - AI model integration and chat
- **LexAPI_Genomics (8001)** - 4.4B genomic record analysis
- **Other Core APIs** - Cross-axis biological analysis

## User Experience Highlights
- **Ancestry-Aware** - Supports global populations with scientifically sound baselines
- **Progressive Enhancement** - Starts with population data, improves with user data
- **Transparent AI** - Shows confidence levels and data sources for all responses
- **Ethical Framework** - Ancestry used for baselines, never discrimination
- **Real-time Analysis** - Access to 4.4B genomic records through conversational AI

## Production Ready
- **Secure** - No sensitive data stored in frontend
- **Scalable** - Stateless frontend with API backend
- **Accessible** - WCAG compliant design
- **Performance** - Optimized for fast loading and smooth interactions
