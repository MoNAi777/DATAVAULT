import openai
from typing import List, Dict, Any, Optional
from config.settings import settings
import json
import re

openai.api_key = settings.openai_api_key


class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def analyze_message(self, content: str, message_type: str = "text") -> Dict[str, Any]:
        """Analyze message content and extract categories, tags, sentiment"""
        try:
            prompt = f"""
            Analyze this message content and provide:
            1. Categories (max 3): crypto, ai-tools, news, personal, work, entertainment, finance, tech, health, travel
            2. Tags (max 5): specific keywords or topics
            3. Sentiment score (-1 to 1): negative to positive
            4. Brief summary (max 50 words)
            
            Message: "{content}"
            Message type: {message_type}
            
            Respond in JSON format:
            {{
                "categories": ["category1", "category2"],
                "tags": ["tag1", "tag2", "tag3"],
                "sentiment": 0.5,
                "summary": "Brief summary here"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                "categories": ["uncategorized"],
                "tags": [],
                "sentiment": 0.0,
                "summary": content[:100] + "..." if len(content) > 100 else content
            }
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for semantic search"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return []
    
    async def query_messages(self, query: str, context_messages: List[Dict]) -> str:
        """Generate response based on query and message context"""
        try:
            # Prepare context from messages
            context = "\n".join([
                f"[{msg.get('timestamp', 'unknown')}] {msg.get('sender_name', 'Unknown')}: {msg.get('content', '')}"
                for msg in context_messages[:10]  # Limit context
            ])
            
            prompt = f"""
            Based on the following message history, answer the user's question comprehensively.
            
            Message History:
            {context}
            
            User Question: {query}
            
            Provide a detailed answer based on the available information. If you can't find specific information, mention what's available and suggest what might be helpful to know.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Query processing error: {e}")
            return "I'm sorry, I encountered an error while processing your query. Please try again."
    
    async def suggest_categories(self, messages: List[Dict]) -> List[str]:
        """Suggest relevant categories based on message content"""
        if not messages:
            return []
        
        # Extract existing categories
        all_categories = []
        for msg in messages:
            if msg.get('categories'):
                all_categories.extend(msg['categories'])
        
        # Count frequency and return top categories
        category_counts = {}
        for cat in all_categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)[:5]
    
    def extract_crypto_mentions(self, text: str) -> List[str]:
        """Extract cryptocurrency mentions from text"""
        # Common crypto patterns
        crypto_patterns = [
            r'\b(?:BTC|Bitcoin)\b',
            r'\b(?:ETH|Ethereum)\b',
            r'\b(?:ADA|Cardano)\b',
            r'\b(?:SOL|Solana)\b',
            r'\b(?:DOT|Polkadot)\b',
            r'\b(?:LINK|Chainlink)\b',
            r'\b(?:MATIC|Polygon)\b',
            r'\b(?:AVAX|Avalanche)\b',
            r'\$[A-Z]{2,10}\b',  # $TOKEN format
        ]
        
        mentions = []
        for pattern in crypto_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            mentions.extend(matches)
        
        return list(set(mentions))  # Remove duplicates 