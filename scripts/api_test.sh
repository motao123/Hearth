#!/bin/bash
# Hearth API Comprehensive Test Script
API=http://localhost:8090
CJAR=/tmp/hearth_cookies.txt
rm -f $CJAR

call() {
  local method=$1 path=$2 data=$3
  if [ -n "$data" ]; then
    curl -s -c $CJAR -b $CJAR -X $method "$API$path" -H 'Content-Type: application/json' -d "$data"
  else
    curl -s -c $CJAR -b $CJAR -X $method "$API$path"
  fi
  echo ""
}

banner() { echo ""; echo "=== $1 ==="; }

banner "1. Register"
call POST /api/auth/register '{"username":"api_test_user","password":"Test1234","name":"API Tester"}'

banner "2. Duplicate Register (should fail)"
call POST /api/auth/register '{"username":"api_test_user","password":"Test1234","name":"API Tester"}'

banner "3. Login"
call POST /api/auth/login '{"username":"api_test_user","password":"Test1234"}'

banner "4. Bad Password (should fail)"
call POST /api/auth/login '{"username":"api_test_user","password":"wrong_pass"}'

banner "5. Get Me"
call GET /api/auth/me

banner "6. List Members"
call GET /api/family/members

banner "7. Add Member"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/family/members" -H 'Content-Type: application/json' -d '{"name":"Test Child","role":"child"}')
echo "$RESP"
CID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "child_id=$CID"

banner "8. Update Member"
call PATCH /api/family/members/$CID '{"name":"Test Child Updated","points":10}'

banner "9. Points Ranking"
call GET /api/family/points

banner "10. Create Task"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/tasks" -H 'Content-Type: application/json' -d '{"title":"Test Task","description":"Testing API","priority":"high"}')
echo "$RESP"
TID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "task_id=$TID"

banner "11. List Tasks"
call GET /api/tasks

banner "12. Update Task"
call PATCH /api/tasks/$TID '{"title":"Updated Task","status":"in_progress"}'

banner "13. Assign Task"
call PATCH /api/tasks/$TID "{\"assignee_id\":$CID}"

banner "14. Complete Task"
call PATCH /api/tasks/$TID '{"status":"done"}'

banner "15. Delete Task"
call DELETE /api/tasks/$TID

banner "16. Create Shopping Item"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/shopping" -H 'Content-Type: application/json' -d '{"name":"Apple","quantity":5,"unit":"pc","category":"Fruit"}')
echo "$RESP"
SID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "shop_id=$SID"

banner "17. List Shopping"
call GET /api/shopping

banner "18. Check Shopping Item"
call PATCH /api/shopping/$SID '{"checked":true,"quantity":3}'

banner "19. Import Shopping from Meals"
call POST /api/shopping/import '{"date":"2026-05-11"}'

banner "20. Clear Checked"
call POST /api/shopping/clear-checked

banner "21. Create Budget Entry"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/budget/entries" -H 'Content-Type: application/json' -d '{"type":"expense","amount":150.00,"category":"Shopping","description":"Groceries"}')
echo "$RESP"
BID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "budget_id=$BID"

banner "22. List Budget"
call GET /api/budget/entries

banner "23. Budget Summary"
call GET /api/budget/summary

banner "24. Update Budget"
call PATCH /api/budget/entries/$BID '{"amount":120.00,"description":"Updated"}'

banner "25. Export CSV"
call GET /api/budget/export?year=2026&month=5

banner "26. Hongbao List"
call GET /api/budget/hongbao

banner "27. Delete Budget"
call DELETE /api/budget/entries/$BID

banner "28. Create Note"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/notes" -H 'Content-Type: application/json' -d '{"title":"Test Note","content":"# Hello\n\n**bold** text","color":"blue"}')
echo "$RESP"
NID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "note_id=$NID"

banner "29. List Notes"
call GET /api/notes

banner "30. Update Note"
call PATCH /api/notes/$NID '{"content":"# Updated\n\nContent changed.","color":"green"}'

banner "31. Delete Note"
call DELETE /api/notes/$NID

banner "32. Create Calendar Event"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/calendar/events" -H 'Content-Type: application/json' -d '{"title":"Family Dinner","date":"2026-05-15","time":"18:00","color":"green","description":"Weekend dinner"}')
echo "$RESP"
EID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "event_id=$EID"

banner "33. List Events"
call GET /api/calendar/events

banner "34. Update Event"
call PATCH /api/calendar/events/$EID '{"title":"Updated Dinner","color":"red"}'

banner "35. Holidays CN"
call GET /api/calendar/holidays/cn?year=2026

banner "36. Lunar Date"
call GET /api/calendar/lunar?date=2026-05-15

banner "37. Delete Event"
call DELETE /api/calendar/events/$EID

banner "38. Create Recipe"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/meals/recipes" -H 'Content-Type: application/json' -d '{"name":"Kung Pao Chicken","description":"Spicy","ingredients":"Chicken\nPeanuts\nChili","steps":"1. Cut\n2. Cook","cooking_time":30,"difficulty":"medium","servings":4}')
echo "$RESP"
RID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "recipe_id=$RID"

banner "39. List Recipes"
call GET /api/meals/recipes

banner "40. Get One Recipe"
call GET /api/meals/recipes/$RID

banner "41. Update Recipe"
call PATCH /api/meals/recipes/$RID '{"name":"Kung Pao Deluxe","cooking_time":25}'

banner "42. Delete Recipe"
call DELETE /api/meals/recipes/$RID

banner "43. Set Meal Plan"
call PUT /api/meals/plan '[{"date":"2026-05-11","slot":"breakfast","title":"Porridge"},{"date":"2026-05-11","slot":"lunch","title":"Noodles"},{"date":"2026-05-11","slot":"dinner","title":"Hotpot"}]'

banner "44. Get Meal Plan"
call GET "/api/meals/plan?start=2026-05-11&end=2026-05-17"

banner "45. Export to Shopping"
call POST /api/meals/export-to-shopping '{"date":"2026-05-11"}'

banner "46. List Files"
call GET /api/files

banner "47. Create Income Budget"
RESP=$(curl -s -c $CJAR -b $CJAR -X POST "$API/api/budget/entries" -H 'Content-Type: application/json' -d '{"type":"income","amount":5000.00,"category":"Salary","description":"Monthly"}')
echo "$RESP"
INC_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
call DELETE /api/budget/entries/$INC_ID

banner "48. Delete Test Child Member"
call DELETE /api/family/members/$CID

banner "49. Logout"
call POST /api/auth/logout

banner "50. Access After Logout (should fail)"
call GET /api/auth/me

banner "51. No Auth Access (should fail)"
rm -f $CJAR
call GET /api/tasks

echo ""
echo "=========================================="
echo "  ALL 51 API TEST POINTS COMPLETED"
echo "=========================================="
