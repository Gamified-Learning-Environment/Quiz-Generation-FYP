# Gamified Learning Environment (GLE) - Quiz Generation Microservice

Welcome to the Quiz Generation Microservice Repository for the Gamified Learning Environment (GLE) project! This microservice handles all quiz creation and management operations, supporting both manual quiz creation and AI-powered quiz generation.

## Service Overview
This microservice is designed to provide personalized learning experiences through interactive and highly customizable quizzes. It supports the platform's objective to enhance online learning engagement through intuitive quiz creation and management.

## Features

### Core Quiz Generation Features

1. Dynamic Quiz Generation:
   - Manual quiz creation interface
   - AI-powered quiz generation using OpenAI
   - User-friendly AI prompt engineering system
   - Customizable quiz parameters and settings

2. Quiz Management:
   - Quiz object creation and persistence
   - Session state management
   - Quiz operation and flow control
   - Question bank management

3. Data Management:
   - Quiz data persistence
   - Integration with results tracking
   - Dynamic feedback generation
   - Quiz performance analytics

## Technologies Used

### Backend Framework
- Flask: Python-based RESTful API development
- MongoDB: Document-based storage for quiz data
  - JSON format for quiz structures
  - Key-value pair storage for efficient retrieval
- OpenAI Integration: AI-powered quiz generation

## API Endpoints

The service exposes RESTful endpoints for:
- Quiz creation (manual and AI-generated)
- Quiz management and retrieval
- Session state handling
- Quiz results submission
- Analytics data access

## System Architecture

### Microservice Integration
This service is one of four independent microservices in the GLE platform:
- User Management
- Quiz Generation (This service)
- Results Tracking
- Gamification

### Communication Flow
- Interfaces with User Management for authentication
- Connects to Results Tracking for performance data
- Integrates with Gamification for achievement tracking
- Utilizes OpenAI API for quiz generation

## Development Status

Current development milestones achieved:
- Dynamic quiz generation system implementation
- Manual and AI-powered quiz creation
- User-friendly AI prompt engineering
- Quiz object management
- Session persistence
- Database schema implementation
- Data flow optimization

  
