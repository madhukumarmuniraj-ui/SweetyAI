# SweetyAI General Intelligence System V2

**Systems that reason, learn, and solve problems across any domain like a human.**

---

## 🧠 Overview

SweetyAI's General Intelligence System V2 is a multi-agent orchestration framework that provides human-like reasoning, learning, and problem-solving capabilities across multiple domains.

## ✨ Key Features

### 1. **Meta-Planning & Reasoning Engine**

The system automatically analyzes every query to determine:

- **Complexity Score** (0.0 - 1.0): Measures task difficulty
  - 0.0-0.3: Simple queries (time, calculator)
  - 0.3-0.6: Moderate tasks (explanations, analysis)
  - 0.6-1.0: Complex problems (design, multi-step reasoning)

- **Domain Classification**: Automatically categorizes queries into:
  - Legal
  - Technical/Programming
  - Scientific
  - Mathematical
  - Creative
  - Business
  - Medical
  - General

- **Adaptive Reasoning Chains**: Generates step-by-step execution plans based on complexity

### 2. **Multi-Agent Specialist System**

Different specialized agents handle different types of tasks:

#### **Meta-Planner Node**
- Analyzes incoming queries
- Determines complexity and domain
- Routes to appropriate specialist
- Generates reasoning chain

#### **Legal Research Agent**
- Specialized in Indian legal statutes
- Uses DSPy optimization when available
- Searches knowledge base for statutory context
- Provides structured legal analysis

#### **Web Research Agent**
- Gathers current information from the web
- Synthesizes findings into coherent answers
- Handles queries requiring up-to-date data

#### **Mathematical Reasoning Agent**
- Step-by-step problem solving
- Calculator integration for expressions
- Shows work and explanations
- High confidence scoring (0.9)

#### **Complex Reasoning Agent**
- Handles multi-step problems
- Uses learned patterns from past successes
- Cross-domain knowledge integration
- Systematic approach with verification

#### **General Reasoning Agent**
- Natural conversation
- Context-aware responses
- Tool execution integration
- Chat history management

#### **Meta-Evaluator Node**
- Final response synthesis
- Quality verification
- Learning extraction
- Metadata compilation

### 3. **Learning Engine (Meta-Learning)**

The system learns from every interaction:

```python
{
  "timestamp": "2026-10-03T16:31:41Z",
  "domain": "mathematical",
  "complexity": 0.65,
  "intent": "mathematical_reasoning",
  "confidence": 0.9,
  "query_pattern": "solve equation <NUM>x^<NUM> + ...",
  "successful": true
}
```

**Capabilities:**
- Stores up to 1000 recent interaction patterns
- Recognizes similar problems
- Recalls successful approaches
- Self-improves confidence over time
- Pattern matching for efficiency

**Storage:** `app/memory/learned_patterns.json`

### 4. **Enhanced Response Metadata**

Every response includes intelligence metrics:

```json
{
  "ok": true,
  "content": "The answer is...",
  "language": "en-IN",
  "intelligence": {
    "domain": "mathematical",
    "complexity": 0.65,
    "confidence": 0.9,
    "reasoning_steps": 5
  }
}
```

## 🔄 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Meta-Planner                               │
│  • Complexity Analysis                                       │
│  • Domain Detection                                          │
│  • Reasoning Chain Generation                                │
│  • Intent Routing                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┬─────────────────┐
      │              │               │                 │
      ▼              ▼               ▼                 ▼
┌─────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────┐
│ Legal   │  │   Web       │  │   Math   │  │   Complex    │
│ Agent   │  │  Research   │  │  Agent   │  │   Reasoning  │
└────┬────┘  └──────┬──────┘  └────┬─────┘  └──────┬───────┘
     │              │               │               │
     └──────────────┴───────────────┴───────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Meta-Evaluator                              │
│  • Response Synthesis                                        │
│  • Quality Verification                                      │
│  • Learning Extraction                                       │
│  • Metadata Compilation                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Learning Engine                             │
│  • Pattern Extraction                                        │
│  • Knowledge Storage                                         │
│  • Confidence Tracking                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Usage Examples

### Simple Query (Complexity: 0.1)
```
User: "What time is it?"
→ Domain: general
→ Agent: general_reasoning_agent
→ Response: "Current Time & Date: 2026-10-03 16:31:41"
```

### Mathematical Query (Complexity: 0.5)
```
User: "Solve the equation 2x + 5 = 15"
→ Domain: mathematical
→ Agent: mathematical_reasoning_agent
→ Reasoning Steps:
   1. Understanding
   2. Calculation
   3. Verification
   4. Synthesis
→ Response: Step-by-step solution with verification
```

### Complex Query (Complexity: 0.8)
```
User: "Design a microservices architecture for e-commerce"
→ Domain: technical
→ Agent: complex_reasoning_agent
→ Reasoning Steps:
   1. Understanding
   2. Knowledge Retrieval
   3. Reasoning
   4. Verification
   5. Synthesis
→ Retrieves similar patterns from learning database
→ Response: Comprehensive architectural design
```

### Legal Query (Complexity: 0.6)
```
User: "What is Section 420 IPC?"
→ Domain: legal
→ Agent: legal_research_agent
→ Searches knowledge base for statutory context
→ Uses DSPy optimization if available
→ Response: Structured legal analysis with provisions
```

## 📊 Confidence Scoring

Each response includes a confidence score indicating certainty:

- **1.0**: Direct tool execution (time, calculator)
- **0.9**: Mathematical reasoning with verification
- **0.85**: Legal analysis with DSPy optimization
- **0.8**: Complex reasoning with pattern matching
- **0.75**: Web research synthesis
- **0.7**: General reasoning/conversation

## 🎯 Reasoning Chain Example

For a complex query, the system generates an adaptive reasoning chain:

```python
[
  {
    "step": "understanding",
    "description": "Parse and understand the user query",
    "status": "complete"
  },
  {
    "step": "knowledge_retrieval",
    "description": "Gather relevant context from knowledge base and tools",
    "status": "complete"
  },
  {
    "step": "reasoning",
    "description": "Apply domain knowledge and logical reasoning",
    "status": "in_progress"
  },
  {
    "step": "verification",
    "description": "Verify reasoning and check for errors",
    "status": "pending"
  },
  {
    "step": "synthesis",
    "description": "Synthesize final response",
    "status": "pending"
  }
]
```

## 🔧 Configuration

The system is automatically activated when `server.py` starts. No additional configuration needed.

### Files Modified:
- `server.py`: Updated to use `build_general_intelligence_graph`
- Added: `app/orchestrator_v2.py` (new intelligence system)
- Created: `app/memory/learned_patterns.json` (learning storage)

## 🧪 Testing

Run the test suite to verify functionality:

```bash
cd C:/SweetyAI
python test_intelligence.py
```

Tests include:
1. Complexity analysis across query types
2. Domain classification accuracy
3. Reasoning chain generation
4. Learning engine pattern matching
5. Graph compilation verification

## 📈 Performance Characteristics

- **Simple Queries**: < 100ms (direct tool execution)
- **Moderate Queries**: 500ms - 2s (single agent)
- **Complex Queries**: 2s - 5s (multiple agents, verification)
- **Learning**: Async, no user-facing delay

## 🔐 Security & Privacy

- All learning patterns are stored locally
- No external data transmission for learning
- Pattern extraction removes personally identifiable information
- Learned patterns contain only structural information

## 🛠️ Maintenance

### Learning Database
- Location: `app/memory/learned_patterns.json`
- Auto-pruned to last 1000 patterns
- Can be manually cleared if needed

### Monitoring
Check system logs for:
- `[Meta-Planner]`: Routing decisions
- `[Learning Engine]`: Pattern storage
- `[Agent]`: Specialist activations
- `[Meta-Evaluator]`: Final synthesis

## 📚 Technical Details

### Dependencies
- `langgraph`: Multi-agent orchestration
- `app.agent.agent.Agent`: Core reasoning engine
- `app.memory`: Chat history management
- `rag.py`: Knowledge base integration
- `app.tools`: Tool execution

### State Management
Uses TypedDict for strong typing:
```python
class GeneralIntelligenceState(TypedDict):
    user_message: str
    complexity_score: float
    domain: str
    reasoning_chain: List[Dict]
    confidence_score: float
    learned_patterns: List[Dict]
    final_response: str
    metadata: Dict
```

## 🎓 Learning From Interactions

The system continuously improves by:
1. Extracting patterns from successful responses
2. Storing complexity and confidence metrics
3. Matching similar queries to past solutions
4. Adapting reasoning strategies based on history

## 🚦 Status

✅ **Active**: General Intelligence System V2 is now operational
✅ **Learning**: Accumulating patterns from interactions
✅ **Multi-Agent**: All specialist agents online
✅ **Backward Compatible**: Works with existing tools and knowledge base

---

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: 2026-10-03  
**Author**: SweetyAI Development Team
