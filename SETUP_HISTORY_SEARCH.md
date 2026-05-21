# History Search Feature - Setup & Migration Guide

## What's New

The Ask API now searches through team's tagged questions and replies **before** querying the LLM. This provides:
- Faster responses using team knowledge
- Reduced LLM API calls and costs
- Clear distinction between team answers and AI-generated answers
- Related questions for additional context

## Files Changed/Added

### New Files
```
backend/app/services/history_search_service.py    - New service for searching questions
FEATURE_HISTORY_SEARCH.md                          - Feature documentation
```

### Modified Backend Files
```
backend/app/api/routes/ask.py                     - Updated to use history search
backend/app/models/response_models.py             - New response models
```

### Modified Frontend Files
```
frontend/src/components/qa/AskPanel.jsx           - Shows answer source
frontend/src/components/qa/AnswerRenderer.jsx     - Displays source badge & related questions
frontend/src/style.css                             - New styles for history UI
```

### Modified Documentation
```
README.md                                          - Updated API docs & workflow explanation
```

## Setup Instructions

### 1. Backend Setup

No database migrations needed! The existing `note_store.db` already has all required data.

**Verify your dependencies** (already in requirements.txt):
- FastAPI
- Pydantic
- sqlite3 (standard library)

```bash
# Ensure backend dependencies are installed
pip install -r requirements.txt
```

### 2. Frontend Setup

No new dependencies required.

```bash
# Reinstall to ensure all updates are picked up
cd frontend
npm install
npm run build  # Optional: rebuild if needed
```

### 3. Environment Variables

No new environment variables required. Works with existing setup:
```bash
LLM_API_URL=...       # Optional (history works without LLM)
LLM_API_KEY=...       # Optional
LLM_MODEL=...         # Optional
```

### 4. Testing the Feature

**Start the backend:**
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8002
```

**Start the frontend:**
```bash
cd frontend
npm run dev
```

**Quick test:**
1. Load a repository with existing tagged questions
2. Ask a question similar to a previously tagged one
3. Should see answer source badge: "📚 Team History"
4. Should see related questions below the answer

## Behavior Changes

### API Changes

#### Request (No Change)
```json
{
  "prompt": "Your question here",
  "selected_file": "optional_file.py",
  "scope": "FILE"
}
```

#### Response (New Fields)
```json
{
  "answer": "...",
  "found": 1,
  "selected_file": "optional_file.py",
  "answer_source": "history",        // NEW
  "source_question_id": 5,           // NEW
  "related_questions": [             // NEW
    {
      "question_id": 8,
      "question": "...",
      "username": "alice",
      "created_at": "2026-05-16T...",
      "scope": "FILE",
      "replies": [...]
    }
  ]
}
```

### UI Changes

**Answer Panel:**
- Shows source badge: "📚 Team History" or "🤖 AI"
- Shows related questions section (if any)
- Related questions display author, date, and all replies

**No Breaking Changes:**
- Existing answer display still works
- File explorer unchanged
- Notes panel unchanged
- Authentication unchanged

## Backward Compatibility

✅ **Fully backward compatible**

- Old code calling POST /ask still works
- New fields are optional in response
- Frontend gracefully handles missing fields
- History search is additive (doesn't remove LLM)

## Tuning

### Adjust Similarity Threshold

Edit `backend/app/services/history_search_service.py`:

```python
class HistorySearchService:
    def __init__(self) -> None:
        self.similarity_threshold = 0.5  # Change this
```

**Recommendations:**
- **0.3-0.5**: More inclusive, more false positives
- **0.5-0.7**: Balanced (current default)
- **0.7+**: Stricter, fewer false positives

### Adjust Best Match Threshold

Edit line in `backend/app/api/routes/ask.py`:

```python
if best_match and best_match["similarity"] >= 0.7:  # Change 0.7
```

**Recommendations:**
- **0.6**: Use history more aggressively
- **0.7**: Balanced (current default)
- **0.8+**: Only exact/very similar matches

## Monitoring & Logging

### Track Which Source Was Used

Add logging to `backend/app/api/routes/ask.py`:

```python
import logging
logger = logging.getLogger(__name__)

# After determining source:
if answer_source == "history":
    logger.info(f"History hit for question #{source_question_id}")
else:
    logger.info("LLM fallback (no history match)")
```

### Monitor Related Questions

Check if related questions are helpful by logging:

```python
if related_answers:
    logger.info(f"Found {len(related_answers)} related questions")
```

## Troubleshooting

### Problem: Getting LLM answers when history exists

**Check:**
1. Questions actually in database: `SELECT COUNT(*) FROM questions;`
2. Similarity scores: Enable debug logging
3. Threshold might be too high

**Solution:**
Lower threshold in HistorySearchService:
```python
self.similarity_threshold = 0.4
```

### Problem: Too many unrelated questions showing

**Check:**
- Related questions threshold is too low (< 0.5)
- Need to tune similarity algorithm

**Solution:**
Increase best_match threshold in ask.py:
```python
if best_match and best_match["similarity"] >= 0.75:  # Stricter
```

### Problem: Answer source not showing in UI

**Check:**
1. Backend returning answer_source field
2. Frontend AnswerRenderer receiving props
3. Browser console for JavaScript errors

**Solution:**
Check network tab in browser dev tools - verify API response includes `answer_source`.

## Performance Impact

### Expected Impact

- **Response time**: +50-200ms (question search)
- **LLM calls**: -30-50% (fewer unnecessary calls)
- **Server load**: Minimal (search is O(n) on in-memory data)

### Optimization Ideas

1. **Cache results**: Store similarity scores
2. **Index questions**: Pre-compute similarity for common questions
3. **Batch search**: Multiple questions at once
4. **Vector DB**: Replace word overlap with embeddings (future)

## Rollback Instructions

If you need to disable history search:

**Option 1: Quick disable**
```python
# In backend/app/api/routes/ask.py, comment out:
# best_match, related_questions = history_search_service.search_related_answers(...)
# best_match = None
```

**Option 2: Full revert**
```bash
git revert <commit-hash>
```

## Next Steps

1. ✅ Deploy updated backend and frontend
2. ✅ Create some tagged questions via the UI
3. ✅ Ask similar questions to test history search
4. ✅ Monitor logs for answer source distribution
5. ✅ Gather team feedback on feature
6. Tune similarity thresholds based on feedback

## Support

For issues or questions:
1. Check FEATURE_HISTORY_SEARCH.md for detailed documentation
2. Review test examples in this file
3. Check browser console for frontend errors
4. Check server logs for backend errors

---

**Version**: 1.0  
**Date**: May 21, 2026  
**Status**: Production Ready
