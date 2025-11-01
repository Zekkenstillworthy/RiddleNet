# MVP Audit Prompt: Essay-Quiz-Class-User Linkage

Use this exact prompt to verify the MVP implementation is complete:

---

## The Prompt

```
MVP audit: Verify Grades, Deadlines, and Essays are fully linked to Quiz, Class contents, and User. 

Acceptance criteria:
1. EssayResponse model has indexes ix_essay_user_id and ix_essay_question_id
2. EssayResponse.question_id has FK constraint to question.id table
3. EssayResponse.user_id has FK constraint to user.id table  
4. Class linkage works via class_students join in instructor.controllers.essay_controller.get_class_essays
5. Grading flow uses EssayResponse.graded_score and is_graded consistently across all API endpoints and templates
6. Deadlines are either persisted server-side with User/Class/Assignment linkage OR deadline UI is feature-flagged off
7. Migration 012_mvp_essay_quiz_linkage.py applies cleanly without errors

Test cases:
- Query essays for class ID 7: GET /instructor/api/essays/class/7 returns grade field
- Grade an essay: POST /instructor/api/essays/<id>/grade updates graded_score and is_graded
- Database integrity: SELECT * FROM essay_response WHERE question_id = X joins to question table
- Performance: Class essay queries complete in < 500ms for 100 students

Expected result: All 7 criteria pass. Deadline criterion is known gap (client-only implementation).
```

---

## Quick Reference

**Files to check:**
- Model: `instructor/models/essay_response.py`
- Controller: `instructor/controllers/essay_controller.py`
- Migration: `migrations/012_mvp_essay_quiz_linkage.py`
- Docs: `MVP_ESSAY_LINKING.md`

**Key endpoints:**
- List class essays: `GET /instructor/api/essays/class/<class_id>`
- Grade essay: `POST /instructor/api/essays/<essay_id>/grade`
- Get essay detail: `GET /instructor/api/essays/<essay_id>`

**Database verification:**
```sql
-- Check indexes exist
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='essay_response';

-- Check FK works
SELECT e.id, e.question_text, q.question 
FROM essay_response e 
JOIN question q ON e.question_id = q.id 
LIMIT 5;

-- Check class linkage
SELECT e.id, e.question_text, u.username, cs.class_id
FROM essay_response e
JOIN user u ON e.user_id = u.id
JOIN class_students cs ON u.id = cs.user_id
WHERE cs.class_id = 7
LIMIT 5;
```

---

## Expected Output

When you run this audit, you should see:
- ✅ Criteria 1-5: **PASS**
- ⚠️ Criterion 6: **KNOWN GAP** (deadlines client-only)
- ✅ Criterion 7: **PASS**

**Overall MVP status:** ✅ **Phase 1 Complete**
