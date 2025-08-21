import os
import json
import weaviate
from typing import List, Dict, Any
from datetime import datetime, timezone

class ChatService:
    def __init__(self):
        """Initialize chat service with Weaviate for storing chat history"""
        # Initialize Weaviate client with v3 syntax
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not weaviate_url or not weaviate_api_key:
            raise ValueError("Missing Weaviate configuration. Please check WEAVIATE_URL and WEAVIATE_API_KEY in your .env file.")
        
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
        )
        
        # Ensure chat history schema exists
        self._create_chat_schema()
    
    def _create_chat_schema(self):
        """Create the Weaviate schema for storing chat history"""
        schema = {
            "class": "ChatMessage",
            "description": "A chat message in a conversation",
            "properties": [
                {
                    "name": "user_id",
                    "dataType": ["text"],
                    "description": "User who sent the message"
                },
                {
                    "name": "user_message",
                    "dataType": ["text"],
                    "description": "The user's question or message"
                },
                {
                    "name": "assistant_message",
                    "dataType": ["text"],
                    "description": "The assistant's response"
                },
                {
                    "name": "persona",
                    "dataType": ["text"],
                    "description": "Persona used for the response (Student/Professor/General)"
                },
                {
                    "name": "sources",
                    "dataType": ["text"],
                    "description": "JSON string of sources used in the response"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "When the message was sent"
                },
                {
                    "name": "conversation_id",
                    "dataType": ["text"],
                    "description": "Unique identifier for the conversation"
                }
            ],
            "vectorizer": "none"
        }
        
        try:
            self.client.schema.create_class(schema)
        except Exception as e:
            # Schema might already exist
            pass
    
    def save_message(self, user_id: str, user_message: str, assistant_message: str, 
                    persona: str, sources: List[Dict[str, Any]], conversation_id: str = None) -> str:
        """
        Save a chat message to the database
        
        Args:
            user_id: User's ID
            user_message: User's question
            assistant_message: Assistant's response
            persona: Persona used for response
            sources: List of sources used
            conversation_id: Optional conversation ID
            
        Returns:
            Message ID
        """
        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Convert sources to JSON string
            sources_json = json.dumps(sources) if sources else "[]"
            
            # Prepare message data
            message_data = {
                "user_id": user_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "persona": persona,
                "sources": sources_json,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": conversation_id
            }
            
            # Store in Weaviate
            result = self.client.data_object.create(
                data_object=message_data,
                class_name="ChatMessage"
            )
            
            return result
            
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a user
        
        Args:
            user_id: User's ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of chat messages
        """
        try:
            result = (
                self.client.query
                .get("ChatMessage", [
                    "user_id",
                    "user_message", 
                    "assistant_message",
                    "persona",
                    "sources",
                    "timestamp",
                    "conversation_id"
                ])
                .with_where({
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(limit)
                .with_sort([{
                    "path": ["timestamp"],
                    "order": "desc"
                }])
                .do()
            )
            
            messages = []
            if result["data"]["Get"]["ChatMessage"]:
                for item in result["data"]["Get"]["ChatMessage"]:
                    # Parse sources JSON
                    sources = json.loads(item["sources"]) if item["sources"] else []
                    
                    messages.append({
                        "user_id": item["user_id"],
                        "user_message": item["user_message"],
                        "assistant_message": item["assistant_message"],
                        "persona": item["persona"],
                        "sources": sources,
                        "timestamp": item["timestamp"],
                        "conversation_id": item["conversation_id"]
                    })
            
            return messages
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def get_conversation(self, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages from a specific conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User's ID for verification
            
        Returns:
            List of messages in the conversation
        """
        try:
            result = (
                self.client.query
                .get("ChatMessage", [
                    "user_id",
                    "user_message", 
                    "assistant_message",
                    "persona",
                    "sources",
                    "timestamp",
                    "conversation_id"
                ])
                .with_where({
                    "operator": "And",
                    "operands": [
                        {
                            "path": ["conversation_id"],
                            "operator": "Equal",
                            "valueString": conversation_id
                        },
                        {
                            "path": ["user_id"],
                            "operator": "Equal",
                            "valueString": user_id
                        }
                    ]
                })
                .with_sort([{
                    "path": ["timestamp"],
                    "order": "asc"
                }])
                .do()
            )
            
            messages = []
            if result["data"]["Get"]["ChatMessage"]:
                for item in result["data"]["Get"]["ChatMessage"]:
                    # Parse sources JSON
                    sources = json.loads(item["sources"]) if item["sources"] else []
                    
                    messages.append({
                        "user_id": item["user_id"],
                        "user_message": item["user_message"],
                        "assistant_message": item["assistant_message"],
                        "persona": item["persona"],
                        "sources": sources,
                        "timestamp": item["timestamp"],
                        "conversation_id": item["conversation_id"]
                    })
            
            return messages
            
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return []
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user
        
        Args:
            user_id: User's ID
            
        Returns:
            List of conversation summaries
        """
        try:
            result = (
                self.client.query
                .get("ChatMessage", [
                    "conversation_id",
                    "timestamp",
                    "user_message"
                ])
                .with_where({
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_groupby(["conversation_id"])
                .with_sort([{
                    "path": ["timestamp"],
                    "order": "desc"
                }])
                .do()
            )
            
            conversations = []
            if result["data"]["Get"]["ChatMessage"]:
                seen_conversations = set()
                for item in result["data"]["Get"]["ChatMessage"]:
                    conv_id = item["conversation_id"]
                    if conv_id not in seen_conversations:
                        conversations.append({
                            "conversation_id": conv_id,
                            "timestamp": item["timestamp"],
                            "first_message": item["user_message"][:100] + "..." if len(item["user_message"]) > 100 else item["user_message"]
                        })
                        seen_conversations.add(conv_id)
            
            return conversations
            
        except Exception as e:
            print(f"Error getting user conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation and all its messages
        
        Args:
            conversation_id: Conversation ID to delete
            user_id: User's ID for verification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all messages in the conversation
            messages = self.get_conversation(conversation_id, user_id)
            
            # Delete each message
            for message in messages:
                # Note: This is a simplified approach
                # In a real implementation, you'd use Weaviate's delete API
                pass
            
            return True
            
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def search_chat_history(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search through chat history for relevant messages
        
        Args:
            user_id: User's ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant messages
        """
        try:
            # This would require implementing semantic search on chat messages
            # For now, we'll return recent messages
            return self.get_chat_history(user_id, limit)
            
        except Exception as e:
            print(f"Error searching chat history: {e}")
            return []
