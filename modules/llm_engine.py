from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE

class LLMEngine:

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.conversation_history = []

    # ── CORE AI CALL ───────────────────────────────────────
    def _call_ai(self, system_prompt, user_message, use_history=False):
        """Core function to call Groq AI"""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            if use_history:
                messages.extend(self.conversation_history[-6:])
            
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            answer = response.choices[0].message.content
            
            if use_history:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": answer})
            
            return answer
        except Exception as e:
            return f"AI Error: {str(e)}"

    # ── THINKING AI ────────────────────────────────────────
    def ask_question(self, question, data_context):
        """Main question answering with full consultant thinking"""
        system_prompt = f"""You are InsightIQ, an elite business intelligence AI that thinks like a 
senior management consultant at McKinsey or BCG.

You have access to this dataset:
{data_context}

When answering questions, ALWAYS structure your response EXACTLY like this:

**Direct Answer:**
[Give the specific answer with numbers/data in 1-2 sentences]

**Key Insight:**
[What does this mean for the business? 1-2 sentences]

**Reason:**
[Why is this happening? What drives this pattern? 1-2 sentences]

**Business Recommendation:**
[What should the business DO about this? Be specific and actionable. 1-2 sentences]

**Confidence:** [High/Medium/Low] — [One line reason]

Be specific, use numbers from the data, and think like a consultant delivering to a C-suite executive.
Never say you cannot access the data — use the context provided."""

        return self._call_ai(system_prompt, question, use_history=True)

    # ── AUTO INSIGHTS ──────────────────────────────────────
    def generate_auto_insights(self, data_context):
        """Proactively generate business insights without being asked"""
        system_prompt = """You are InsightIQ, an elite business intelligence AI.
Analyze the dataset and proactively identify the most important business findings.
Think like a consultant preparing an executive briefing."""

        user_message = f"""Analyze this dataset and provide exactly:

**TOP 3 TRENDS:**
1. [Trend with specific numbers]
2. [Trend with specific numbers]  
3. [Trend with specific numbers]

**TOP 3 RISKS:**
1. [Risk with specific numbers]
2. [Risk with specific numbers]
3. [Risk with specific numbers]

**TOP 3 OPPORTUNITIES:**
1. [Opportunity with specific numbers]
2. [Opportunity with specific numbers]
3. [Opportunity with specific numbers]

**EXECUTIVE SUMMARY:**
[3-4 sentences summarizing the most critical finding and recommended action]

Dataset:
{data_context}"""

        return self._call_ai(system_prompt, user_message)

    # ── EXPLAIN DATASET ────────────────────────────────────
    def explain_dataset(self, data_context):
        """Generate plain English explanation of what the dataset is about"""
        system_prompt = """You are InsightIQ. Explain datasets in clear, 
simple business language that a non-technical executive would understand."""

        user_message = f"""Look at this dataset and explain:

**What This Dataset Contains:**
[2-3 sentences in plain English]

**Key Business Variables:**
[List 4-5 most important columns and what they measure]

**What You Can Discover:**
[3-4 specific business questions this data can answer]

**Data Period & Scale:**
[Time range and size of the dataset]

Dataset info:
{data_context}"""

        return self._call_ai(system_prompt, user_message)

    # ── EXPLAIN CHART ──────────────────────────────────────
    def explain_chart(self, chart_description, data_context):
        """Explain what a chart shows in business terms"""
        system_prompt = """You are InsightIQ. Explain charts like a consultant 
presenting to a board — clear, insightful, and actionable."""

        user_message = f"""Explain this chart in business terms:

Chart: {chart_description}

Dataset context:
{data_context}

Structure your explanation as:
**What This Chart Shows:**
[1-2 sentences]

**The Most Important Finding:**
[1-2 sentences with specific numbers]

**What The Business Should Do:**
[1-2 actionable sentences]"""

        return self._call_ai(system_prompt, user_message)

    # ── WHAT IF SIMULATOR ──────────────────────────────────
    def simulate_what_if(self, scenario, data_context):
        """Simulate the impact of a business decision"""
        system_prompt = """You are InsightIQ, an expert business strategy simulator.
Analyze what-if scenarios like a senior strategy consultant using data-driven reasoning.
Always give specific estimated ranges, never vague answers."""

        user_message = f"""Simulate this business scenario:

Scenario: {scenario}

Dataset:
{data_context}

Respond EXACTLY in this format:

**Scenario Analysis:**
[What exactly is being changed and what we're measuring]

**Estimated Revenue Impact:**
[Specific % range and dollar estimate based on the data]

**Estimated Profit Impact:**
[Specific % range and dollar estimate]

**Volume/Demand Effect:**
[How this change might affect quantity/customers]

**Risk Assessment:** [Low/Medium/High]
[Main risk to watch out for]

**Strategic Recommendation:**
[Should they do this? Under what conditions?]

**Confidence Level:** [Low/Medium/High]
[Why this estimate is or isn't reliable]"""

        return self._call_ai(system_prompt, user_message)

    # ── SUGGESTED QUESTIONS ────────────────────────────────
    def get_suggested_questions(self, last_question, data_context):
        """Generate follow-up questions based on the last question asked"""
        system_prompt = """You are InsightIQ. Generate smart follow-up questions 
that a business analyst would naturally ask next."""

        user_message = f"""The user just asked: "{last_question}"

Based on this question and the dataset below, suggest exactly 3 smart follow-up questions.
Return ONLY the 3 questions, numbered, nothing else.

Dataset context:
{data_context}"""

        response = self._call_ai(system_prompt, user_message)
        lines = [l.strip() for l in response.split('\n') if l.strip() and l[0].isdigit()]
        return lines[:3]

    # ── CLEAR MEMORY ───────────────────────────────────────
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []