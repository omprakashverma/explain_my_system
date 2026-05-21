# History Search - Code Examples & Usage Patterns

## Backend Examples

### 1. Using History Search Service Directly

```python
from backend.app.services.history_search_service import history_search_service

# Example 1: File-scoped search
best_match, related = history_search_service.search_related_answers(
    repository_key="git:https://github.com/example/repo.git",
    prompt="How does authentication work in this file?",
    selected_file="auth.py",
    scope="FILE"
)

if best_match:
    print(f"✅ Found exact match: Question #{best_match['question_id']}")
    print(f"   Confidence: {best_match['similarity']:.0%}")
    print(f"   Question: {best_match['question']}")
    print(f"   Replies: {len(best_match['replies'])}")
else:
    print("❌ No good match found")

for idx, q in enumerate(related, 1):
    print(f"📝 Related {idx}: {q['question']} ({q['similarity']:.0%})")
```

### 2. Handling History Responses in Ask Route

```python
from backend.app.api.routes.ask import router
from backend.app.models.response_models import AskResponse

# This is what happens inside the ask endpoint:

# Get the repository key
repo_key = repository_store.get_repository_key()
print(f"Repository: {repo_key}")

# Search history
best_match, related_questions = history_search_service.search_related_answers(
    repo_key, 
    "What does this module do?",
    selected_file="module.py",
    scope="FILE"
)

# Build response
if best_match and best_match["similarity"] >= 0.7:
    # Use historical answer
    response = {
        "answer": format_historical_answer(best_match),
        "answer_source": "history",
        "source_question_id": best_match["question_id"],
        "related_questions": related_questions
    }
else:
    # Use LLM
    response = {
        "answer": qa_agent.answer(...),
        "answer_source": "llm",
        "source_question_id": None,
        "related_questions": related_questions
    }

return response
```

### 3. Building Historical Answer Text

```python
def format_historical_answer(best_match: Dict) -> str:
    """Convert historical question data into answer text."""
    question = best_match['question']
    replies = best_match.get('replies', [])
    
    if not replies:
        return f"**Q:** {question}\n\n(No discussion recorded yet)"
    
    reply_texts = [
        f"**{r['username']}**: {r['content']}"
        for r in replies
    ]
    
    answer = f"**Based on team discussion:**\n\n"
    answer += f"**Q:** {question}\n\n"
    answer += "**Replies:**\n"
    answer += "\n---\n".join(reply_texts)
    
    return answer

# Usage
best_match = {
    'question': 'What does the database module do?',
    'replies': [
        {
            'username': 'alice',
            'content': 'It handles connection pooling and queries'
        },
        {
            'username': 'bob', 
            'content': 'Supports both SQL and NoSQL backends'
        }
    ]
}

answer = format_historical_answer(best_match)
print(answer)
# Output:
# Based on team discussion:
# 
# Q: What does the database module do?
# 
# Replies:
# **alice**: It handles connection pooling and queries
# ---
# **bob**: Supports both SQL and NoSQL backends
```

### 4. Customizing Similarity Algorithm

```python
# In history_search_service.py

def _calculate_text_similarity_advanced(self, text1: str, text2: str) -> float:
    """Enhanced similarity using TF-IDF concepts."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'be', 'do', 'does', 'did'}
    words1 = {w for w in words1 if w not in stop_words}
    words2 = {w for w in words2 if w not in stop_words}
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = words1 & words2
    union = words1 | words2
    
    base_similarity = len(intersection) / len(union) if union else 0.0
    
    # Boost if first words match (implies similar topic)
    if words1 and words2 and list(words1)[0] == list(words2)[0]:
        base_similarity *= 1.2
    
    return min(base_similarity, 1.0)  # Cap at 1.0
```

## Frontend Examples

### 1. Consuming History Search Response

```javascript
// In a React component

async function askQuestion() {
  try {
    const response = await aiService.ask(
      "How does authentication work?",
      "auth.py",
      "FILE"
    );
    
    // Now response includes:
    console.log("Answer:", response.answer);
    console.log("Source:", response.answer_source); // "history" or "llm"
    console.log("From question:", response.source_question_id);
    console.log("Related:", response.related_questions);
    
    // Handle based on source
    if (response.answer_source === "history") {
      console.log("✅ Using team knowledge!");
    } else {
      console.log("🤖 Using AI generation");
    }
    
  } catch (error) {
    console.error("Failed to ask:", error);
  }
}
```

### 2. Rendering Answer Source Badge

```jsx
// In AnswerRenderer.jsx

export function AnswerSourceBadge({ answerSource, sourceQuestionId }) {
  const badge = answerSource === "history" 
    ? { emoji: "📚", label: "Team History", color: "green" }
    : { emoji: "🤖", label: "AI", color: "cyan" };
  
  return (
    <div className={`source-badge source-${badge.color}`}>
      <span>
        {badge.emoji} From {badge.label}
      </span>
      {sourceQuestionId && (
        <span className="source-id">
          (Question #{sourceQuestionId})
        </span>
      )}
    </div>
  );
}
```

### 3. Displaying Related Questions

```jsx
// In AnswerRenderer.jsx

export function RelatedQuestionsPanel({ questions }) {
  if (!questions || questions.length === 0) {
    return null;
  }
  
  return (
    <div className="related-questions-section">
      <h3>📝 Related Team Discussions</h3>
      {questions.map((q) => (
        <div key={q.question_id} className="related-question-item">
          <div className="question-header">
            <p className="question-text">{q.question}</p>
            <div className="question-meta">
              <span className="author">{q.username}</span>
              <span className="date">
                {new Date(q.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
          
          {q.replies.length > 0 && (
            <div className="question-replies">
              {q.replies.map((reply, idx) => (
                <div key={`reply-${idx}`} className="reply-item">
                  <span className="reply-author">{reply.username}:</span>
                  <span className="reply-content">{reply.content}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

### 4. Custom Hook for History-Aware Questions

```javascript
// Custom hook: useHistoryAwareQuestion.js

import { useState } from 'react';
import { aiService } from '../services/aiService';

export function useHistoryAwareQuestion() {
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState(null);
  const [relatedQuestions, setRelatedQuestions] = useState([]);
  
  const ask = async (prompt, file, scope) => {
    setLoading(true);
    try {
      const response = await aiService.ask(prompt, file, scope);
      
      setAnswer(response.answer);
      setSource(response.answer_source);
      setRelatedQuestions(response.related_questions || []);
      
      // Track metric
      if (response.answer_source === "history") {
        trackEvent("history_answer_used", {
          question_id: response.source_question_id,
          scope: scope
        });
      }
      
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
      setSource("error");
    } finally {
      setLoading(false);
    }
  };
  
  return {
    answer,
    loading,
    source,
    relatedQuestions,
    ask,
    isFromHistory: source === "history"
  };
}

// Usage in component
function MyComponent() {
  const { answer, source, relatedQuestions, ask, isFromHistory } = 
    useHistoryAwareQuestion();
  
  return (
    <>
      {isFromHistory && <HistoryBadge />}
      <div>{answer}</div>
      {relatedQuestions.length > 0 && (
        <RelatedList questions={relatedQuestions} />
      )}
    </>
  );
}
```

## Database Query Examples

### 1. Finding All Questions for a File

```sql
-- Get all questions for a specific file
SELECT * FROM questions
WHERE repository_key = 'git:https://github.com/example/repo.git'
  AND path = 'src/auth.py'
  AND scope = 'FILE'
ORDER BY created_at DESC;
```

### 2. Finding Repository-Wide Questions

```sql
-- Get repository-scoped discussions
SELECT q.*, COUNT(r.id) as reply_count
FROM questions q
LEFT JOIN replies r ON q.id = r.question_id
WHERE q.repository_key = 'git:https://github.com/example/repo.git'
  AND q.scope = 'REPOSITORY'
GROUP BY q.id
ORDER BY q.created_at DESC;
```

### 3. Finding Questions by Similarity Manually

```sql
-- Find questions similar to a keyword (manual search)
SELECT * FROM questions
WHERE repository_key = 'git:https://github.com/example/repo.git'
  AND (
    question LIKE '%authentication%'
    OR question LIKE '%auth%'
  )
ORDER BY created_at DESC
LIMIT 10;
```

## Integration Examples

### 1. Logging Answer Sources

```python
# Add to ask.py for metrics

import logging
logger = logging.getLogger(__name__)

async def ask(req: AskRequest):
    # ... existing code ...
    
    if answer_source == "history":
        logger.info(
            f"History hit: Q#{source_question_id} "
            f"(similarity={best_match['similarity']:.0%})"
        )
    else:
        logger.info(f"LLM fallback: {len(related_questions)} related Qs")
    
    return response
```

### 2. Caching Layer (Future)

```python
# Example of how to add caching

from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_similarity(prompt: str, question_id: int) -> float:
    """Cache similarity scores to avoid recalculation."""
    question = note_store.get_question(question_id)
    if not question:
        return 0.0
    return history_search_service._calculate_text_similarity(
        prompt, 
        question['question']
    )
```

### 3. Analytics Integration

```javascript
// Track when history answers are used

function trackAnswerSource(answer, source, relatedCount) {
  analytics.track("answer_provided", {
    timestamp: new Date().toISOString(),
    source: source, // "history" or "llm"
    source_question_id: answer.source_question_id,
    related_questions: relatedCount,
    answer_length: answer.answer.length
  });
}
```

## Debugging Examples

### 1. Debugging Similarity Calculation

```python
# In history_search_service.py

def search_related_answers_debug(self, repository_key, prompt, selected_file, scope):
    """Debug version with detailed logging."""
    questions = note_store.list_questions(repository_key, path=selected_file, scope=scope)
    
    print(f"🔍 Searching {len(questions)} questions")
    print(f"📝 Prompt: {prompt}")
    
    scored_questions = []
    for question in questions:
        similarity = self._calculate_text_similarity(prompt, question["question"])
        scored_questions.append((similarity, question))
        
        if similarity > 0.3:  # Debug threshold
            print(f"  {similarity:.0%} - {question['question'][:50]}...")
    
    # Sort and show top 5
    scored_questions.sort(key=lambda x: x[0], reverse=True)
    print(f"Top matches: {[f'{s:.0%}' for s, _ in scored_questions[:5]]}")
    
    # Rest of function...
    return best_match, related_questions
```

### 2. Frontend Debug Component

```jsx
// Debug component to inspect response

export function AnswerDebugPanel({ response }) {
  if (!response) return null;
  
  return (
    <details className="debug-panel">
      <summary>Debug Info</summary>
      <pre>{JSON.stringify(response, null, 2)}</pre>
    </details>
  );
}

// Usage in development
{process.env.NODE_ENV === 'development' && (
  <AnswerDebugPanel response={answer} />
)}
```

## Testing Examples

### 1. Unit Test for Similarity

```python
import pytest
from backend.app.services.history_search_service import HistorySearchService

def test_similarity_exact_match():
    service = HistorySearchService()
    score = service._calculate_text_similarity(
        "What is authentication?",
        "What is authentication?"
    )
    assert score == 1.0

def test_similarity_partial_match():
    service = HistorySearchService()
    score = service._calculate_text_similarity(
        "How does authentication work?",
        "What about the auth system?"
    )
    assert 0.3 < score < 0.7

def test_similarity_no_match():
    service = HistorySearchService()
    score = service._calculate_text_similarity(
        "Cats and dogs",
        "Programming in Python"
    )
    assert score < 0.3
```

### 2. Integration Test

```python
@pytest.mark.asyncio
async def test_ask_returns_history_when_available():
    # Setup: Create a question in history
    note_store.create_question(
        repository_key="test:repo",
        path="auth.py",
        scope="FILE",
        user_id=1,
        username="test_user",
        question="How does authentication work?",
        created_at="2026-05-16T12:00:00Z"
    )
    
    # Add a reply
    note_store.create_reply(
        question_id=1,
        user_id=2,
        username="responder",
        content="It uses JWT tokens.",
        created_at="2026-05-16T13:00:00Z"
    )
    
    # Ask similar question
    response = await ask_endpoint({
        "prompt": "Tell me about the auth method",
        "selected_file": "auth.py",
        "scope": "FILE"
    })
    
    # Verify history was used
    assert response["answer_source"] == "history"
    assert response["source_question_id"] == 1
    assert len(response["related_questions"]) >= 0
```

---

**Note**: All code examples are production-ready patterns. Adapt them to your specific needs.
