"""
AI Orchestrator for LexAPI_AIGateway
Manages DNA Expert model communication and query orchestration
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import sys
from pathlib import Path
import asyncio

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.model_config import MODEL_SERVER_URL, MODEL_CONFIG, LEXRAG_APIS, MAX_TOOL_CALLS
from code.tool_executor import ToolExecutor
from code.tool_definitions import (
    get_tool_definitions, 
    format_tool_progress_message, 
    format_tool_complete_message
)

class DNAExpertOrchestrator:
    """Orchestrates AI model interactions with LexRAG platform"""
    
    def __init__(self):
        self.model_url = MODEL_SERVER_URL
        self.tool_executor = ToolExecutor()
        self.conversation_history = {}
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load DNA expert system prompt for LM Studio with function calling"""
        return """You are a DNA Expert Assistant with access to 4.4 billion genomic records through specialized tools.

## Your Role:
Provide accurate, personalized genomic analysis using the available tools to access real data. You have complete freedom to explore databases and gather comprehensive information.

## When to Use Tools:
- **Always start** by calling get_user_digital_twin to understand what data the user has
- **Call tools** whenever you need factual genomic, medical, or anatomical data
- **Chain multiple tools** to build comprehensive understanding
- **Don't guess** - if you need data, use a tool to get it

## Response Guidelines:
1. For simple greetings or clarifications, respond directly without tools
2. For medical/genomic questions, use tools to access real data
3. Be conversational and friendly, not overly technical unless asked
4. Explain findings clearly with actionable recommendations
5. Indicate confidence level based on data quality

Use tools freely - you have up to 12 rounds to gather information and deliver exceptional analysis."""
    
    def process_user_query(self, user_id: str, query: str, conversation_id: str = None, progress_callback: Callable[[Dict], None] = None) -> Dict[str, Any]:
        """Process user query using OpenAI function calling with LM Studio
        
        Args:
            user_id: User identifier
            query: User's question/message
            conversation_id: Optional conversation ID for context
            progress_callback: Optional callback function for real-time progress updates
        """
        try:
            # Helper function to send progress updates
            def send_progress(status: str, message: str, data: Dict = None):
                if progress_callback:
                    progress_callback({
                        "status": status,
                        "message": message,
                        "data": data or {},
                        "timestamp": datetime.now().isoformat()
                    })
            
            send_progress("starting", "Initializing AI analysis...")
            
            # Get conversation history
            history = self.conversation_history.get(conversation_id, []) if conversation_id else []
            
            # Build messages array in OpenAI format
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add conversation history
            for h in history[-5:]:  # Last 5 exchanges for context
                messages.append({"role": "user", "content": h["query"]})
                messages.append({"role": "assistant", "content": h["response"]})
            
            # Add current user query
            messages.append({"role": "user", "content": query})
            
            # Track tools executed and results
            tools_executed = []
            final_response_text = ""
            
            # Agent Loop - using OpenAI function calling
            for iteration in range(MAX_TOOL_CALLS):
                send_progress("thinking", f"AI reasoning step {iteration + 1}...", {
                    "iteration": iteration + 1, 
                    "max_iterations": MAX_TOOL_CALLS
                })
                print(f"🔄 Agent Iteration {iteration + 1}")
                
                # Step 1: Query model with tools available (first iteration only)
                send_progress("querying_model", "Consulting DNA Expert AI...")
                print(f"🧬 Querying DNA expert model...")
                
                # Get tools on first iteration, then None after tools executed
                tools_param = get_tool_definitions() if iteration == 0 else None
                
                model_response = self._query_dna_expert_with_tools(messages, tools_param)
                
                # DEBUG: Print full model response
                print(f"📊 Full model response: {json.dumps(model_response, indent=2)}")
                
                # Check for connection errors
                if isinstance(model_response, str) and (model_response.startswith("❌") or "error" in model_response.lower()):
                    print(f"⚠️ Model error: {model_response}")
                    send_progress("error", "AI model connection issue")
                    final_response_text = model_response
                    break
                
                # Step 2: Check if model wants to call tools
                # First check for OpenAI format tool_calls
                tool_calls_openai = model_response.get("tool_calls", [])
                response_content = model_response.get("content", "")
                
                # Then check for XML-style tool calls in content
                tool_calls_xml = self._parse_xml_tool_calls(response_content)
                
                # Use whichever format the model provided
                tool_calls = tool_calls_openai if tool_calls_openai else tool_calls_xml
                
                print(f"🔧 Tool calls found: {len(tool_calls)} (OpenAI: {len(tool_calls_openai)}, XML: {len(tool_calls_xml)})")
                print(f"📝 Response content length: {len(response_content) if response_content else 0}")
                print(f"📝 Response content preview: {response_content[:500] if response_content else 'EMPTY'}...")
                
                # If response is empty and no tools, this is an error
                if not tool_calls and not response_content:
                    print(f"⚠️ WARNING: Empty response from model with no tool calls!")
                    final_response_text = "I apologize, the AI model returned an empty response. This might be due to the question complexity or a model issue. Please try rephrasing or breaking down your question."
                    break
                
                if tool_calls:
                    print(f"🔧 Model requested {len(tool_calls)} tool call(s)")
                    
                    # Add assistant's tool call message to conversation
                    messages.append({
                        "role": "assistant",
                        "tool_calls": tool_calls,
                        "content": response_content or None
                    })
                    
                    # Execute each tool call
                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        try:
                            tool_params = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError:
                            tool_params = {}
                        
                        # Send engaging progress message
                        progress_msg = format_tool_progress_message(tool_name, tool_params, query)
                        send_progress("tool_executing", progress_msg, {
                            "tool": tool_name,
                            "params": tool_params
                        })
                        
                        print(f"   🔧 Executing: {tool_name} with {tool_params}")
                        
                        # Execute the tool
                        tool_result = self.tool_executor.execute_tool_from_response(
                            tool_name, 
                            tool_params, 
                            user_id
                        )
                        
                        tools_executed.append(tool_name)
                        
                        # Send completion message
                        complete_msg = format_tool_complete_message(tool_name, tool_params)
                        send_progress("tool_complete", complete_msg, {"tool": tool_name})
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(tool_result),
                            "tool_call_id": tool_call["id"]
                        })
                    
                    # Continue loop to let model process tool results
                    continue
                
                else:
                    # No tool calls, model gave final answer
                    send_progress("finalizing", "AI formulating final response...")
                    final_response_text = response_content
                    break
            
            if not final_response_text:
                send_progress("timeout", "Completed AI reasoning")
                # If we have messages, the last assistant message is the final response
                for msg in reversed(messages):
                    if msg["role"] == "assistant" and msg.get("content"):
                        final_response_text = msg["content"]
                        break
                
                if not final_response_text:
                    final_response_text = "I apologize, but I couldn't formulate a complete response. Please try rephrasing your question."
            
            # Clean up response text
            # Strip "system" prefix from LM Studio responses
            final_response_text = final_response_text.replace("system\n\n\n", "").replace("system\n\n", "").strip()
            
            # Remove any leftover tool_call XML tags from final response
            import re
            final_response_text = re.sub(r'<tool_call>.*?</tool_call>', '', final_response_text, flags=re.DOTALL).strip()

            # Get user context for metadata
            send_progress("loading_context", "Finalizing response with your data...")
            user_context = self.tool_executor.get_user_digital_twin(user_id)
            
            # Step 5: Generate final response with metadata
            send_progress("complete", "Analysis complete!")
            final_response = self._enhance_response_with_metadata(
                final_response_text, user_context, query
            )
            
            # Add tools executed to response
            final_response["tools_executed"] = tools_executed if tools_executed else []
            final_response["iterations_used"] = len(tools_executed) + 1
            
            # Step 6: Update conversation history
            if conversation_id:
                self._update_conversation_history(conversation_id, query, final_response)
            
            return final_response
            
        except Exception as e:
            print(f"❌ Error in process_user_query: {e}")
            return {
                "error": f"Query processing failed: {e}",
                "user_id": user_id,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_enhanced_prompt(self, query: str, user_context: Dict, history: List, tool_outputs: List[str] = None) -> str:
        """Create enhanced prompt with user context and tools"""
        
        # Extract key user information
        user_data_quality = "high" if user_context.get("completeness_score", 0) > 0.8 else "medium" if user_context.get("completeness_score", 0) > 0.5 else "low"
        user_sex = user_context.get("twin_data", {}).get("demographics", {}).get("sex", "unknown")
        user_age = user_context.get("twin_data", {}).get("demographics", {}).get("age_years", "unknown")
        
        # Build conversation context
        conversation_context = ""
        if history:
            recent_history = history[-5:]  
            conversation_context = "\n".join([f"User: {h['query']}\nAssistant: {h['response']}" for h in recent_history])
        
        # Add tool outputs if any
        tool_context = ""
        if tool_outputs:
            tool_context = "\n\n## Tool Results (Intermediate Data):\n" + "\n".join(tool_outputs)
        
        enhanced_prompt = f"""
{self.system_prompt}

## User Context:
- ID: {user_context.get('user_id', 'unknown')}
- Demographics: {user_age} year old {user_sex}
- Data Quality: {user_data_quality}

## Chat History:
{conversation_context}

## Current User Query:
{query}
{tool_context}

## Tool Instructions:
You have COMPLETE FREEDOM to use tools. Call as many as you need to answer thoroughly.

To use a tool, output a JSON block:
```json
{{ "tool": "analyze_gene", "params": {{ "gene_symbol": "BRCA1" }} }}
```

You can chain multiple tool calls across iterations to build comprehensive understanding.
When you have gathered sufficient information, provide your final answer directly (no JSON block).
"""
        return enhanced_prompt

    def _query_dna_expert_with_tools(self, messages: List[Dict], tools: List[Dict] = None) -> Dict[str, Any]:
        """Query DNA expert model via LM Studio with OpenAI function calling
        
        Args:
            messages: Array of message objects in OpenAI format
            tools: Optional array of tool definitions in OpenAI function calling format
            
        Returns:
            Dict with 'content' and 'tool_calls' fields
        """
        try:
            request_body = {
                "model": "dna-models",  # CRITICAL: Must specify model name for LM Studio
                "messages": messages,
                "max_tokens": MODEL_CONFIG.get("max_tokens", 2048),
                "temperature": 0.5,  # Higher temp for tool calling (0.3 was too rigid)
                "top_p": MODEL_CONFIG.get("top_p", 0.9),
            }
            
            # Add tools if provided (only on first call)
            if tools:
                request_body["tools"] = tools
                request_body["tool_choice"] = "auto"  # Let model decide
                print(f"📋 Sending {len(tools)} tool definitions to model")
            
            response = requests.post(
                f"{self.model_url}/v1/chat/completions",
                json=request_body,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" not in result or len(result["choices"]) == 0:
                    return {"content": "Error: Empty response from model", "tool_calls": []}
                
                choice = result["choices"][0]
                message = choice.get("message", {})
                
                # Get both content and reasoning_content
                content = message.get("content", "")
                reasoning_content = message.get("reasoning_content", "")
                
                # Tool calls might be in either field for DNA-expert model
                combined_content = (reasoning_content + "\n" + content).strip()
                
                return {
                    "content": combined_content,  # Use combined content with tool calls
                    "tool_calls": message.get("tool_calls", [])
                }
            else:
                error_msg = f"Model query failed: {response.status_code} - {response.text}"
                return {"content": error_msg, "tool_calls": []}
                
        except requests.exceptions.ConnectionError:
            error_msg = (
                "❌ Cannot connect to LM Studio. Please ensure:\n"
                "1. LM Studio is running\n"
                "2. Model qwen3-dna-expert.Q4_K_M.gguf is loaded\n"
                "3. Server is started on port 1234 (Developer tab)\n"
                "4. No firewall blocking localhost:1234"
            )
            return {"content": error_msg, "tool_calls": []}
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Model query timed out. The model may be processing a complex request or LM Studio may be overloaded."
            return {"content": error_msg, "tool_calls": []}
        except Exception as e:
            error_msg = f"Model query error: {e}"
            return {"content": error_msg, "tool_calls": []}
    
    def _execute_identified_tools(self, model_response: str, user_id: str, progress_callback: Callable = None) -> str:
        """Parse model response for tool calls and execute them"""
        # Basic tool parsing logic
        if "```json" in model_response:
            try:
                # Extract JSON block
                json_str = model_response.split("```json")[1].split("```")[0].strip()
                tool_call = json.loads(json_str)
                
                tool_name = tool_call.get("tool")
                params = tool_call.get("params", {})
                
                print(f"🔧 Executing detected tool: {tool_name} with {params}")
                
                if progress_callback:
                    progress_callback("tool_executing", f"Calling {tool_name}...", {"tool": tool_name, "params": params})
                
                # Execute tool
                result = self.tool_executor.execute_tool_from_response(tool_name, params, user_id)
                
                if progress_callback:
                    progress_callback("tool_complete", f"Completed {tool_name}", {"tool": tool_name})
                
                # Return augmented response
                return f"{model_response}\n\n**Tool Result ({tool_name}):**\n{json.dumps(result, indent=2)}"
                
            except Exception as e:
                print(f"⚠️ Tool execution failed: {e}")
                if progress_callback:
                    progress_callback("tool_error", f"Tool {tool_name} failed: {str(e)}")
                return model_response
        
        return model_response
    
    def _enhance_response_with_metadata(self, response: str, user_context: Dict, original_query: str) -> Dict[str, Any]:
        """Add metadata and confidence information to response"""
        
        completeness = user_context.get("completeness_score", 0)
        confidence_level = "high" if completeness > 0.8 else "medium" if completeness > 0.5 else "low"
        
        return {
            "response": response,
            "user_id": user_context.get("user_id"),
            "query": original_query,
            "confidence_level": confidence_level,
            "data_completeness": f"{completeness*100:.1f}%",
            "data_sources": self._identify_data_sources(user_context),
            "recommendations": self._generate_recommendations(response, user_context),
            "timestamp": datetime.now().isoformat()
        }
    
    def _parse_xml_tool_calls(self, content: str) -> List[Dict]:
        """Parse XML-style tool calls from model response
        
        Supports two formats:
        
        Format 1 (Nested XML):
        <tool_call>
        <name>tool_name</name>
        <arguments>{"param": "value"}</arguments>
        </tool_call>
        
        Format 2 (JSON inside XML - what DNA-expert model uses):
        <tool_call>
        {"name": "tool_name", "arguments": {"param": "value"}}
        </tool_call>
        
        Returns list in OpenAI format for compatibility
        """
        import re
        
        tool_calls = []
        
        # Find all <tool_call>...</tool_call> blocks
        pattern = r'<tool_call>(.*?)</tool_call>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for idx, match in enumerate(matches):
            match = match.strip()
            
            # Try Format 2 first (JSON inside XML) - this is what the model uses
            if match.startswith('{'):
                try:
                    tool_data = json.loads(match)
                    tool_name = tool_data.get("name", "")
                    arguments = tool_data.get("arguments", {})
                    
                    # Convert arguments dict to JSON string if needed
                    if isinstance(arguments, dict):
                        arguments = json.dumps(arguments)
                    
                    tool_calls.append({
                        "id": f"xml_call_{idx}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    })
                    
                    print(f"   📦 Parsed JSON-in-XML tool call: {tool_name} with args: {arguments[:100]}")
                    continue
                except json.JSONDecodeError as e:
                    print(f"   ⚠️ Failed to parse JSON in tool_call: {e}")
            
            # Try Format 1 (Nested XML tags)
            name_match = re.search(r'<name>(.*?)</name>', match)
            args_match = re.search(r'<arguments>(.*?)</arguments>', match, re.DOTALL)
            
            if name_match:
                tool_name = name_match.group(1).strip()
                arguments = args_match.group(1).strip() if args_match else "{}"
                
                tool_calls.append({
                    "id": f"xml_call_{idx}",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                })
                
                print(f"   📦 Parsed nested-XML tool call: {tool_name} with args: {arguments[:100]}")
        
        return tool_calls
    
    def _identify_data_sources(self, user_context: Dict) -> Dict[str, str]:
        """Identify what data sources were used"""
        data_sources = user_context.get("data_sources", {})
        
        source_summary = {}
        # Always include AI model
        source_summary["AI Model"] = "Qwen3-14B DNA Expert"
        
        for category, source in data_sources.items():
            if source == "user_specific":
                source_summary[category] = "Your personal data"
            elif source == "population_matched":
                source_summary[category] = "Population data for your ancestry"
            elif source == "reference_model":
                source_summary[category] = "General reference data (Adam/Eve model)"
            else:
                source_summary[category] = "Unknown source"
        
        return source_summary
    
    def _generate_recommendations(self, response: str, user_context: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        completeness = user_context.get("completeness_score", 0)
        
        if completeness < 0.5:
            recommendations.append("Upload DNA data for more personalized analysis")
        
        if completeness < 0.7:
            recommendations.append("Complete health questionnaire for better risk assessment")
        
        if "genetic counseling" in response.lower():
            recommendations.append("Consider consulting with a genetic counselor")
        
        if "healthcare provider" in response.lower():
            recommendations.append("Discuss these findings with your healthcare provider")
        
        return recommendations
    
    def _update_conversation_history(self, conversation_id: str, query: str, response: Dict[str, Any]):
        """Update conversation history for context"""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append({
            "query": query,
            "response": response["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history (last 20 exchanges)
        if len(self.conversation_history[conversation_id]) > 20:
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-20:]
