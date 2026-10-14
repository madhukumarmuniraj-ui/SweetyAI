"""
Test script for SweetyAI General Intelligence System V2
Demonstrates reasoning, learning, and cross-domain problem-solving
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_general_intelligence():
    """Test the new General Intelligence System"""

    print("="*70)
    print("SweetyAI General Intelligence System V2 - Test Suite")
    print("="*70)

    # Test 1: Complexity Analysis
    print("\n[TEST 1] Complexity Analysis")
    from app.orchestrator_v2 import ReasoningEngine

    test_queries = [
        "What time is it?",
        "Calculate 5 + 3",
        "Explain quantum entanglement and how it relates to information theory",
        "Design a scalable microservices architecture for an e-commerce platform"
    ]

    for query in test_queries:
        complexity = ReasoningEngine.analyze_complexity(query)
        domain = ReasoningEngine.identify_domain(query)
        print(f"\nQuery: {query[:60]}...")
        print(f"  → Complexity: {complexity:.2f}/1.0")
        print(f"  → Domain: {domain}")

    # Test 2: Domain Identification
    print("\n\n[TEST 2] Domain Classification")
    domain_tests = [
        ("What is Section 420 IPC?", "legal"),
        ("Write a Python function to sort arrays", "technical"),
        ("Explain Einstein's theory of relativity", "scientific"),
        ("Solve the equation: 2x + 5 = 15", "mathematical"),
        ("Write a haiku about the moon", "creative"),
        ("What's a good marketing strategy?", "business")
    ]

    for query, expected in domain_tests:
        detected = ReasoningEngine.identify_domain(query)
        status = "✓" if detected == expected else "✗"
        print(f"{status} {query[:40]:45s} → {detected:15s} (expected: {expected})")

    # Test 3: Reasoning Chain Generation
    print("\n\n[TEST 3] Reasoning Chain Generation")
    complex_query = "Analyze the legal implications of AI-generated content under copyright law"
    complexity = ReasoningEngine.analyze_complexity(complex_query)
    domain = ReasoningEngine.identify_domain(complex_query)
    chain = ReasoningEngine.generate_reasoning_chain(complex_query, domain, complexity)

    print(f"\nQuery: {complex_query}")
    print(f"Complexity: {complexity:.2f} | Domain: {domain}")
    print("\nReasoning Chain Steps:")
    for i, step in enumerate(chain, 1):
        print(f"  {i}. {step['step']:20s} - {step['description']}")

    # Test 4: Learning Engine
    print("\n\n[TEST 4] Learning Engine")
    from app.orchestrator_v2 import LearningEngine

    learning_engine = LearningEngine()
    print(f"Loaded {len(learning_engine.patterns)} existing patterns")

    # Simulate a learning interaction
    test_state = {
        'timestamp': '2026-10-03T16:31:14Z',
        'domain': 'mathematical',
        'complexity_score': 0.6,
        'intent': 'mathematical_reasoning',
        'confidence_score': 0.9,
        'user_message': 'Solve quadratic equation x^2 + 5x + 6 = 0'
    }

    learning_engine.learn_from_interaction(test_state)
    print(f"After learning: {len(learning_engine.patterns)} patterns")

    # Test pattern matching
    similar = learning_engine.get_similar_patterns(
        "Solve equation 2x^2 + 3x - 5 = 0",
        "mathematical"
    )
    print(f"Found {len(similar)} similar patterns for equation solving")

    # Test 5: Graph Compilation
    print("\n\n[TEST 5] Graph Compilation")
    try:
        from app.main import load_model
        from app.agent.agent import Agent
        from app.orchestrator_v2 import build_general_intelligence_graph

        print("Loading model...")
        tokenizer, model = load_model()
        agent = Agent(model=model, tokenizer=tokenizer)

        print("Compiling General Intelligence Graph...")
        sweety_app = build_general_intelligence_graph(agent)

        print("✓ Graph compiled successfully!")
        print(f"  Graph type: {type(sweety_app)}")

        # Show available nodes
        print("\n  Available Reasoning Nodes:")
        nodes = ['meta_planner', 'legal_agent', 'web_agent', 'math_agent',
                 'complex_agent', 'general_agent', 'meta_evaluator']
        for node in nodes:
            print(f"    • {node}")

    except Exception as e:
        print(f"✗ Graph compilation failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("Test Suite Complete!")
    print("="*70)

if __name__ == "__main__":
    test_general_intelligence()
