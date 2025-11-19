# Real-Time Updates Guide for Manage Tolis Dashboard

## Problem Solved
The manage tolis dashboard was showing old/cached programs and not updating when students created new programs. Now it shows real-time data with automatic updates.

---

## Changes Made

### 1. **Backend API Endpoint** (app/routes/admin.py)

#### New API Endpoint Added:
```python
@admin.route('/admin/toli/<toli_id>/programs')
```

**Location:** End of app/routes/admin.py (around line 1847)

**What it does:**
- Fetches fresh programs directly from MongoDB for a specific toli
- Returns JSON with program details (title, type, location, date, status)
- No caching - always gets latest data

**API Response Format:**
```json
{
  "success": true,
  "programs": [
    {
      "id": "program_id",
      "title": "Program Title",
      "program_type": "Yagya/Yoga/etc",
      "location": "City, State",
      "start_date": "01 Jan 2024",
      "status": "pending/completed",
      "total_persons": 50,
      "created_at": "01 Jan 2024 10:30"
    }
  ],
  "count": 5
}
```

---

### 2. **Frontend Updates** (app/templates/admin/manage_toli.html)

#### A. Updated Programs Section HTML
- Added refresh button to manually update programs
- Added `id="programsList"` for JavaScript to update
- Added status badges (green for completed, yellow for pending)
- Added total programs counter

#### B. New JavaScript Function: `refreshPrograms()`

**What it does:**
1. Calls the API endpoint `/admin/toli/<toli_id>/programs`
2. Gets fresh program data
3. Updates the programs list on the page
4. Updates the program count in the header
5. Shows visual feedback (green flash) when updated

**Features:**
- Shows only 5 most recent programs
- Displays status badges with colors
- Animates when new data arrives
- Updates program count in real-time

#### C. Automatic Updates
- Programs refresh every 30 seconds automatically
- Also refreshes when you switch back to the tab
- Manual refresh button available

---

## How Data Flows (Student → Admin)

### When Student Creates a Program:

1. **Student Side** (app/routes/student.py - create_program route)
   ```python
   program_data = {
       'toli_id': current_user.toli_id,  # ← Links to toli
       'student_id': current_user.id,
       'title': form.title.data,
       # ... other fields
   }
   db.create_program(program_dict)
   ```

2. **Database** (app/database.py)
   ```python
   def create_program(self, program_data):
       return self.db.programs.insert_one(program_data)
   ```
   - Program saved to MongoDB with toli_id

3. **Admin Dashboard Fetches**
   ```python
   def get_programs_by_toli(self, toli_id):
       return list(self.db.programs.find({'toli_id': toli_id}))
   ```
   - Queries MongoDB for all programs with matching toli_id

4. **API Returns Fresh Data**
   - No caching
   - Direct database query
   - Real-time results

5. **Frontend Updates**
   - JavaScript calls API every 30 seconds
   - Updates UI with new programs
   - Shows visual feedback

---

## How to Use the APIs

### API 1: Get Toli Programs
**Endpoint:** `GET /admin/toli/<toli_id>/programs`

**Example:**
```javascript
// Fetch programs for toli with ID "abc123"
const response = await fetch('/admin/toli/abc123/programs');
const data = await response.json();

console.log(data.programs); // Array of programs
console.log(data.count);    // Total count
```

**Use Cases:**
- Display programs list
- Check if new programs added
- Get program statistics

---

### API 2: Get Toli Stats
**Endpoint:** `GET /admin/toli/<toli_id>/stats`

**Example:**
```javascript
const response = await fetch('/admin/toli/abc123/stats');
const data = await response.json();

console.log(data.member_count);  // Number of members
console.log(data.program_count); // Number of programs
console.log(data.status);        // Toli status
```

**Use Cases:**
- Update dashboard counters
- Monitor toli activity
- Real-time statistics

---

## Testing the Real-Time Updates

### Test Scenario 1: Create New Program
1. Open admin manage toli page in one browser tab
2. Open student dashboard in another tab (same toli)
3. Student creates a new program
4. Wait 30 seconds OR click "Refresh" button on admin page
5. ✅ New program appears in the list
6. ✅ Program count increases

### Test Scenario 2: Manual Refresh
1. Open manage toli page
2. Click the "Refresh" button (🔄 icon)
3. ✅ Programs list updates immediately
4. ✅ Green flash animation shows update

### Test Scenario 3: Automatic Updates
1. Open manage toli page
2. Leave it open for 30+ seconds
3. ✅ Stats update automatically
4. ✅ Programs refresh automatically
5. ✅ Timestamps show "Updated: HH:MM:SS"

---

## Where to Find Each Component

### Backend Files:
```
app/routes/admin.py
├── Line ~1847: New API endpoint /admin/toli/<toli_id>/programs
├── Line ~1437: Existing API /admin/toli/<toli_id>/stats
└── Line ~420: Main manage_toli route

app/database.py
├── Line ~193: get_programs_by_toli() method
└── Line ~192: create_program() method

app/routes/student.py
└── Line ~782: create_program route (saves toli_id)
```

### Frontend Files:
```
app/templates/admin/manage_toli.html
├── Line ~130: Programs section HTML
├── Line ~450: refreshPrograms() JavaScript function
├── Line ~380: updateToliStats() JavaScript function
└── Line ~550: Auto-update initialization
```

---

## Troubleshooting

### Programs Not Showing?
**Check:**
1. Is `toli_id` saved when student creates program?
   ```python
   # In student.py create_program route
   print(f"Creating program with toli_id: {current_user.toli_id}")
   ```

2. Is database query working?
   ```python
   # In database.py
   programs = db.get_programs_by_toli(toli_id)
   print(f"Found {len(programs)} programs for toli {toli_id}")
   ```

3. Check browser console for errors:
   - Open DevTools (F12)
   - Look for API errors
   - Check network tab for failed requests

### Updates Not Happening?
**Check:**
1. JavaScript console for errors
2. Network tab - is API being called?
3. Check if toli_id matches between student and admin

### API Returns Empty?
**Check:**
1. Verify toli_id is correct
2. Check if programs exist in database:
   ```javascript
   db.programs.find({toli_id: "your_toli_id"})
   ```
3. Ensure student's toli_id matches

---

## Summary

✅ **What's Fixed:**
- Programs now update in real-time
- No more stale/cached data
- Automatic refresh every 30 seconds
- Manual refresh button available
- Visual feedback when data updates

✅ **How It Works:**
- Student creates program → Saves with toli_id
- Admin page calls API → Gets fresh data from MongoDB
- JavaScript updates UI → Shows new programs
- Automatic polling → Keeps data fresh

✅ **APIs Available:**
1. `/admin/toli/<toli_id>/programs` - Get programs list
2. `/admin/toli/<toli_id>/stats` - Get toli statistics

✅ **Update Frequency:**
- Automatic: Every 30 seconds
- Manual: Click refresh button anytime
- On tab focus: When you return to the page
