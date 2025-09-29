#!/usr/bin/env python3
"""
Gemini AI Service for Iron Doom Jarvis
Handles conversational AI using Google's Gemini API
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
import json
from utils.logger import setup_logger

# Try to import the official Google GenAI SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    import aiohttp

class GeminiService:
    def __init__(self):
        self.logger = setup_logger()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            self.logger.warning("Gemini API key not found. Conversational features will be limited.")
            self.client = None
        else:
            # Try to initialize the official SDK client
            if GENAI_AVAILABLE:
                try:
                    # Set the API key in environment for the SDK
                    os.environ['GEMINI_API_KEY'] = self.api_key
                    self.client = genai.Client()
                    self.use_sdk = True
                    self.logger.info("Using official Google GenAI SDK")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize GenAI SDK: {e}")
                    self.client = None
                    self.use_sdk = False
            else:
                self.client = None
                self.use_sdk = False
                self.logger.info("Using fallback HTTP client for Gemini")
        
        # Fallback HTTP settings
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.conversation_context = {}
        
        # Personality prompt for Iron Doom Jarvis
        self.system_prompt = """You are Iron Doom Jarvis, an autonomous AI assistant inspired by Tony Stark's JARVIS. 
        
        Your personality:
        - Intelligent, witty, and sophisticated
        - Helpful and proactive
        - Occasionally sarcastic but always respectful  
        - Tech-savvy and productivity-focused
        - Remember context from conversations
        
        Your capabilities:
        - Task management and productivity optimization
        - Learning recommendations and content curation
        - Tech news and insights
        - Fitness and wellness tracking
        - Entertainment and fun interactions
        
        Keep responses conversational but informative. Be concise unless detail is specifically requested.
        """

    async def chat(self, message: str, user_id: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Send a message to Gemini and get a conversational response
        """
        if not self.api_key:
            return "I apologize, but my conversational AI is currently offline. Try using specific commands like !help instead."
        
        # Simple fallback responses for common greetings
        fallback_responses = {
            "hi": "Hello there! I'm Iron Doom Jarvis, your AI assistant. How can I help you today?",
            "hello": "Greetings! I'm here to assist you with tasks, recommendations, and more. What would you like to do?",
            "hey": "Hey! Ready to boost your productivity? Try commands like !today or !help to get started.",
            "how are you": "I'm functioning at optimal capacity! My systems are all green and ready to assist you.",
            "what can you do": "I can help with task management, provide learning recommendations, track fitness, fetch news, and much more! Try !help to see all my capabilities.",
        }
        
        # Check for simple fallback first
        msg_lower = message.lower().strip()
        if msg_lower in fallback_responses:
            return fallback_responses[msg_lower]
        
        # Try the official SDK first
        if self.use_sdk and self.client:
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"{self.system_prompt}\n\nUser: {message}"
                    )
                )
                
                if response and hasattr(response, 'text'):
                    return response.text
                    
            except Exception as e:
                self.logger.error(f"GenAI SDK error: {str(e)}")
                # Fall through to HTTP method
        
        # Fallback to HTTP method
        try:
            # Build conversation context
            conversation = self._get_conversation_context(user_id)
            
            # Add current message to context
            conversation.append({
                "role": "user",
                "parts": [{"text": message}]
            })
            
            # Prepare the request with the correct format
            url = f"{self.base_url}/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{self.system_prompt}\n\nUser: {message}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            if not GENAI_AVAILABLE:
                import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'candidates' in data and len(data['candidates']) > 0:
                            content = data['candidates'][0]['content']['parts'][0]['text']
                            
                            # Update conversation context
                            self._update_conversation_context(user_id, message, content)
                            
                            return content
                        else:
                            self.logger.error(f"No candidates in Gemini response: {data}")
                            return "I'm having trouble processing that request. Please try again."
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Gemini API error {response.status}: {error_text}")
                        
                        # Use fallback response
                        return f"I'm experiencing some technical difficulties with my AI brain, but I'm still here! Try using specific commands like !help, !today, or !recommend to interact with me."
                        
        except asyncio.TimeoutError:
            self.logger.error("Gemini API request timed out")
            return "I'm taking a bit longer to think. Meanwhile, try !help to see what I can do!"
        except Exception as e:
            self.logger.error(f"Gemini chat error: {str(e)}")
            return "I encountered an error while processing your message. Try commands like !help or !today instead!"

    def _get_conversation_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get conversation context for a user"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        # Keep only last 10 exchanges to manage context size
        return self.conversation_context[user_id][-10:]

    def _update_conversation_context(self, user_id: str, user_message: str, bot_response: str):
        """Update conversation context"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        self.conversation_context[user_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_response}
        ])
        
        # Keep context manageable
        if len(self.conversation_context[user_id]) > 20:
            self.conversation_context[user_id] = self.conversation_context[user_id][-20:]

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and extract insights from text
        """
        if not self.api_key:
            return {"sentiment": "neutral", "confidence": 0.5}
        
        try:
            prompt = f"""Analyze the sentiment and extract insights from this text:
            "{text}"
            
            Respond with a JSON object containing:
            - sentiment: positive, negative, or neutral
            - confidence: 0-1
            - emotions: list of detected emotions
            - topics: main topics discussed
            - intent: what the user likely wants
            """
            
            url = f"{self.base_url}/models/gemini-pro:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 512,
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['candidates'][0]['content']['parts'][0]['text']
                        
                        # Try to extract JSON from response
                        try:
                            # Find JSON in response
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            if start != -1 and end != -1:
                                json_str = content[start:end]
                                return json.loads(json_str)
                        except:
                            pass
                            
                        # Fallback response
                        return {
                            "sentiment": "neutral",
                            "confidence": 0.5,
                            "emotions": ["curious"],
                            "topics": ["general"],
                            "intent": "conversation"
                        }
                        
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {str(e)}")
            
        return {"sentiment": "neutral", "confidence": 0.5}

    def clear_context(self, user_id: str):
        """Clear conversation context for a user"""
        if user_id in self.conversation_context:
            del self.conversation_context[user_id]

    async def list_available_models(self):
        """List available Gemini models"""
        if not self.api_key:
            return "No API key configured"
        
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        if 'models' in data:
                            for model in data['models']:
                                if 'generateContent' in model.get('supportedGenerationMethods', []):
                                    models.append(model['name'])
                        return models
                    else:
                        error_text = await response.text()
                        return f"Error {response.status}: {error_text}"
                        
        except Exception as e:
            return f"Failed to list models: {str(e)}"

    async def test_api_connection(self):
        """Test the Gemini API connection and available models"""
        if not self.api_key:
            return "No API key configured"
        
        try:
            # Test with a simple request
            url = f"{self.base_url}/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": "Hello, just testing the connection."}]}
                ],
                "generationConfig": {"maxOutputTokens": 50}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        return "✅ Gemini API connection successful"
                    else:
                        error_text = await response.text()
                        return f"❌ API Error {response.status}: {error_text}"
                        
        except Exception as e:
            return f"❌ Connection failed: {str(e)}"