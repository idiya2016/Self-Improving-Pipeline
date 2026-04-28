# ====================================================================
# Groq API - Static vs Adaptive Self-Improving Pipeline
# Author: Diya Chavda
# Course: COT6930 - Generative Intelligence
# ====================================================================

from groq import Groq
import time
import json

# ====================================================================
# SECTION 1: API CONFIGURATION
# ====================================================================

API_KEY = "YOUR_GROQ_API_KEY_HERE"
client = Groq(api_key=API_KEY)

# ====================================================================
# SECTION 2: MODEL SETUP
# ====================================================================
# Generator: Smaller model (starts with lower scores, needs improvement)
MODEL_GENERATE = "llama-3.1-8b-instant"

# Evaluator: Powerful model (accurate scoring)
MODEL_EVALUATE = "llama-3.3-70b-versatile"

# ====================================================================
# SECTION 3: PROMPT CONFIGURATION
# ====================================================================
INITIAL_PROMPT = """
Summarize the following article in exactly 50 words. 
You must include:
- At least 2 specific numbers
- At least 6 proper names (people, companies, or mission names)
- The exact year mentioned

Use only factual statements. No opinions. No adjectives like "exciting" or "important".
Be extremely precise. Word count must be exactly 50.
"""

# ====================================================================
# SECTION 4: TEST ARTICLES
# ====================================================================

ARTICLE_1 = """
The City of Boca Raton has been recognized as a 2025 Tree City USA for the 46th consecutive year. 
It also received the Growth Award for the seventh year. The city supports urban forestry through 
tree planting, community events, and conservation efforts. Trees help reduce heat, improve air quality, 
and enhance property value. An Arbor Day event will plant 40 trees at a local park.
"""

ARTICLE_2 = """
Warner Bros. Discovery shareholders approved a major acquisition involving Paramount, marking a significant shift in the media industry. 
The deal reflects ongoing consolidation as companies compete in streaming and global entertainment markets. Analysts say the merger could 
reshape content distribution, though concerns remain about regulation, competition, and long-term profitability.
"""

ARTICLE_3 = """
NASA's Artemis II mission will send astronauts around the Moon to test spacecraft systems, including life support and docking capabilities. 
The mission is part of a broader plan to return humans to the Moon and eventually reach Mars. Artemis III is expected to attempt a lunar landing, 
though delays and technical challenges remain. NASA is also working with private companies to develop necessary infrastructure.
"""

# ====================================================================
# SECTION 5: GENERATION FUNCTION
# ====================================================================

def generate(prompt, temperature=0.9):
    """Send prompt to Groq and get response"""
    response = client.chat.completions.create(
        model=MODEL_GENERATE,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content

# ====================================================================
# SECTION 6: EVALUATOR FUNCTION
# ====================================================================

def evaluate(article, summary):
    """Score the summary using a rubric"""
    
    rubric = """
    Score the summary from 0 to 100 based on these three criteria:
    
    - Conciseness (40 points): Is the summary brief and to the point? No fluff or unnecessary words.
    - Factuality (40 points): Does the summary contain ONLY information from the article? No hallucinations or made-up facts.
    - Clarity (20 points): Is the summary well written, grammatically correct, and easy to understand?
    
    Return ONLY valid JSON in this exact format:
    {"score": int, "reasoning": "one sentence explanation"}
    
    Do not include any other text outside the JSON.
    """
    
    prompt = f"{rubric}\n\n--- ARTICLE ---\n{article}\n\n--- SUMMARY ---\n{summary}"
    
    response = client.chat.completions.create(
        model=MODEL_EVALUATE,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    result_text = response.choices[0].message.content.strip()
    result_text = result_text.replace('```json', '').replace('```', '').strip()
    
    try:
        result = json.loads(result_text)
        return result.get("score", 50), result.get("reasoning", "No reasoning provided")
    except json.JSONDecodeError:
        return 50, "Could not parse evaluator response"

# ====================================================================
# SECTION 7: PROMPT IMPROVEMENT FUNCTION
# ====================================================================

def improve_prompt(old_prompt, score, reasoning, last_summary):
    """Generate an improved prompt based on feedback"""
    
    prompt = f"""
    You are a prompt engineer. Improve the following summary prompt based on the feedback.
    
    OLD PROMPT: "{old_prompt}"
    
    LAST SUMMARY GENERATED: "{last_summary[:300]}"
    
    SCORE RECEIVED: {score}/100
    
    FEEDBACK FROM EVALUATOR: "{reasoning}"
    
    Write a NEW, IMPROVED prompt that addresses the issues mentioned in the feedback.
    Keep it concise and direct. Output ONLY the new prompt text, nothing else.
    """
    
    response = client.chat.completions.create(
        model=MODEL_EVALUATE,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

# ====================================================================
# SECTION 8: STATIC PIPELINE
# ====================================================================

def run_static(article, prompt, iterations=3):
    """Static pipeline: same prompt every time, no learning"""
    print(f"\n--- STATIC PIPELINE ---")
    results = []
    
    for i in range(iterations):
        print(f"  Iteration {i+1}:")
        
        summary = generate(f"{prompt}\n\nArticle:\n{article}")
        score, reasoning = evaluate(article, summary)
        
        print(f"    Score: {score}")
        print(f"    Summary: {summary[:150]}...")
        
        results.append({
            "iteration": i+1,
            "score": score,
            "summary": summary,
            "reasoning": reasoning
        })
        
        time.sleep(1)
    
    return results

# ====================================================================
# SECTION 9: ADAPTIVE SELF-IMPROVING PIPELINE
# ====================================================================

def run_adaptive(article, initial_prompt, max_iterations=3, target_score=85):
    """Adaptive pipeline: prompt improves based on feedback each iteration"""
    print(f"\n--- ADAPTIVE PIPELINE (Self-Improving) ---")
    
    current_prompt = initial_prompt
    results = []
    
    for i in range(max_iterations):
        print(f"  Iteration {i+1}:")
        
        summary = generate(f"{current_prompt}\n\nArticle:\n{article}")
        score, reasoning = evaluate(article, summary)
        
        print(f"    Score: {score}")
        print(f"    Summary: {summary[:150]}...")
        print(f"    Feedback: {reasoning[:100]}...")
        
        results.append({
            "iteration": i+1,
            "prompt": current_prompt,
            "score": score,
            "summary": summary,
            "reasoning": reasoning
        })
        
        if score >= target_score:
            print(f"    ✅ Target {target_score} reached! Stopping early.")
            break
        
        if i < max_iterations - 1:
            current_prompt = improve_prompt(current_prompt, score, reasoning, summary)
            print(f"    New prompt generated")
        
        time.sleep(1)
    
    return results

# ====================================================================
# SECTION 10: MAIN EXPERIMENT LOOP (Temperature 0.7)
# ====================================================================

print("=" * 70)
print("GROQ EXPERIMENT: Static vs Adaptive (Self-Improving) Pipeline")
print(f"Generator Model: {MODEL_GENERATE}")
print(f"Evaluator Model: {MODEL_EVALUATE}")
print("Temperature: 0.7")
print("=" * 70)

all_results = {}

articles = [
    (ARTICLE_1, "Article 1 - Boca Raton"),
    (ARTICLE_2, "Article 2 - Media Merger"),
    (ARTICLE_3, "Article 3 - NASA")
]

for idx, (article, name) in enumerate(articles, 1):
    print(f"\n{'='*70}")
    print(f"EXPERIMENT {idx}: {name}")
    print(f"{'='*70}")
    
    static_results = run_static(article, INITIAL_PROMPT, iterations=3)
    adaptive_results = run_adaptive(article, INITIAL_PROMPT, max_iterations=3, target_score=85)
    
    all_results[name] = {
        "static": static_results,
        "adaptive": adaptive_results
    }
    
    static_best = max([r['score'] for r in static_results])
    adaptive_best = max([r['score'] for r in adaptive_results])
    
    print(f"\n  Static best score: {static_best}")
    print(f"  Adaptive best score: {adaptive_best}")

# ====================================================================
# SECTION 11: RESULTS OUTPUT
# ====================================================================

print("\n" + "=" * 70)
print("FINAL COMPARISON TABLE")
print("=" * 70)
print(f"\n{'Article':<25} {'Static Best':<12} {'Adapt Best':<12} {'Iterations':<10}")
print("-" * 65)

for name, results in all_results.items():
    static_best = max([r['score'] for r in results['static']])
    adaptive_best = max([r['score'] for r in results['adaptive']])
    adapt_iterations = len(results['adaptive'])
    
    print(f"{name:<25} {static_best:<12} {adaptive_best:<12} {adapt_iterations:<10}")

print("\n" + "=" * 70)
print("DETAILED ITERATION SCORES")
print("=" * 70)

for name, results in all_results.items():
    print(f"\n{name}:")
    print(f"  Static:      {[r['score'] for r in results['static']]}")
    print(f"  Adaptive:    {[r['score'] for r in results['adaptive']]}")
