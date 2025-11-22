# Testing Guide for UI Improvements

## Quick Start
1. Navigate to http://localhost:3000
2. Upload a test video (any presentation will work)
3. Wait for analysis to complete

---

## What to Test

### 1. Smart Segmentation
**Expected**: Segments should align with natural breaks in speech, not arbitrary 10 chunks

**How to Verify**:
- Go to Delivery Metrics tab
- Check timeline chart - segments should be variable length
- Hover over data points to see segment info
- Each segment should have a text preview that shows actual spoken content

**What to Look For**:
- Segments start/end at sentence boundaries
- Segments are 20-50 words (natural chunks)
- Number of segments varies based on video length (not always 10!)

---

### 2. Key Moments Tab
**Expected**: See 2-6 cards total (good clips + bad clips)

**How to Verify**:
- Click "Key Moments" tab (2nd tab)
- Should see "Strong Moments" section with green cards (if any segments have confidence ≥75%)
- Should see "Needs Improvement" section with red cards (if any segments have confidence <60%)
- Click "▶ Watch This Moment" or "▶ Watch & Learn" button

**What to Look For**:
- Clip player opens in overlay (doesn't switch tabs)
- Video starts at correct timestamp
- Video auto-pauses at end of clip
- Can close with ✕ button
- Each card shows:
  - Confidence score
  - Text preview
  - Explanation of why it's good/bad
  - Timestamp and duration

---

### 3. Confidence Transparency
**Expected**: Clear explanation of how confidence is calculated

**How to Verify**:
- Go to Delivery Metrics tab
- Look for "📊 How Confidence is Calculated" card at top
- Should see formula explanation
- Should see breakdown of 3 factors: Pacing, Filler Control, Structure

**What to Look For**:
- Formula shows: "Confidence = Pacing (±20) + Filler Control (±30) + Clear Structure (±10) from base of 70. Range: 0-100."
- Each factor has icon, title, and description
- Makes sense to non-technical users

---

### 4. Weakest/Strongest Moments
**Expected**: Visual callout of extremes with details

**How to Verify**:
- Go to Delivery Metrics tab
- Look below confidence explanation
- Should see 2 cards side-by-side:
  - Left: "⚠️ Weakest Moment" (red gradient)
  - Right: "✅ Strongest Moment" (green gradient)

**What to Look For**:
- Shows segment number
- Shows confidence score (large, colored)
- Shows text preview
- Shows explanation (e.g., "✓ Perfect pace (145 WPM) | ✗ Too many fillers")

---

### 5. Better Timeline Chart
**Expected**: Area chart showing confidence flow, not dual bar chart

**How to Verify**:
- Go to Delivery Metrics tab
- Scroll to "Performance Timeline" section
- Should see green gradient area chart

**What to Look For**:
- X-axis: Segment numbers (variable count, not always 1-10)
- Y-axis: Confidence (0-100%)
- Green gradient fill under line
- Hover to see tooltip with:
  - Segment number
  - Confidence %
  - WPM
  - Filler count
  - Confidence explanation text

**What Should NOT Be There**:
- ❌ Dual Y-axis bar chart with "Speaking Pace & Filler Words"
- ❌ Two separate charts

---

### 6. Video Performance
**Expected**: Smooth playback, no lag

**How to Verify**:
- Go to Overview tab
- Play video
- Seek to different timestamps
- Try clip playback from Key Moments tab

**What to Look For**:
- Video loads quickly (preload metadata)
- No stuttering during playback
- Seeking is smooth (not constant micro-seeks)
- Clip player starts at exact timestamp
- Clip player stops at end timestamp

**What Should NOT Happen**:
- ❌ Video feels slowed down
- ❌ Constant buffering or lag
- ❌ Seeking causes jump/stutter

---

### 7. Reduced Nesting
**Expected**: Cleaner UI, less cluttered

**How to Verify**:
- Inspect overall feel of interface
- Check if cards are easier to scan

**What to Look For**:
- Flatter visual hierarchy
- Less "card inside card inside card"
- More breathing room

---

## Sample Test Scenarios

### Scenario 1: Short Video (1-2 min)
**Expected Results**:
- 4-8 segments (not 10)
- May not have bad clips if presentation is good overall
- Timeline should show meaningful patterns

### Scenario 2: Long Video (5+ min)
**Expected Results**:
- 15-30+ segments (varies based on content)
- Likely has both good and bad clips
- Timeline shows clear trends

### Scenario 3: High Filler Count
**Expected Results**:
- Bad clips should highlight segments with many fillers
- Confidence explanation should mention "✗ Too many fillers (X, Y% of words)"
- Weakest moment card should explain filler issue

### Scenario 4: Perfect Delivery
**Expected Results**:
- Only good clips (no bad clips)
- High confidence scores (80-100%)
- Explanations show "✓ Perfect pace", "✓ No filler words", etc.

---

## Common Issues & Solutions

### Issue: "Key Moments tab is empty"
**Cause**: No segments meet thresholds (≥75% for good, <60% for bad)  
**Solution**: This is correct behavior! Means presentation is consistently mediocre (60-74% confidence)

### Issue: "Video won't play"
**Cause**: Video URL issue or CORS  
**Solution**: Check browser console for errors. Verify `http://localhost:8000/api/video/{session_id}` works

### Issue: "Clip doesn't auto-stop"
**Cause**: Event listener issue  
**Solution**: Check ClipReview.js useEffect cleanup

### Issue: "Timeline shows 10 segments"
**Cause**: Old cached data from previous version  
**Solution**: Clear browser cache and re-upload video

---

## Browser Console Checks

Open browser dev tools (F12) and look for:

### Expected Console Output (Good):
```
No errors
Network requests to /api/upload succeed (200 OK)
/api/video/{id} returns video data
```

### Errors to Watch For (Bad):
```
❌ 404 on /api/video/{id} - Video serving broken
❌ Uncaught TypeError in ClipReview - Component issue
❌ Failed to load recharts - Chart library issue
```

---

## Performance Benchmarks

### Video Load Time:
- **Target**: <2 seconds for metadata load
- **Measure**: Check Network tab in dev tools for `/api/video/{id}` request time

### Chart Rendering:
- **Target**: <500ms for timeline chart to render
- **Measure**: Should be instant when switching to Delivery Metrics tab

### Clip Playback:
- **Target**: <1 second to start playback when clicking "Watch This Moment"
- **Measure**: Time from button click to video playing

---

## API Response Structure (For Debugging)

When you upload a video, `/api/upload` should return:

```json
{
  "results": {
    "confidence_score": 72,
    "confidence_explanation": "Confidence = Pacing (±20) + Filler Control (±30) + Clear Structure (±10) from base of 70. Range: 0-100.",
    "timeline": [
      {
        "segment": 1,
        "wpm": 145,
        "confidence": 85,
        "confidence_explanation": "✓ Perfect pace (145 WPM) | ✓ No filler words | ✓ Clear sentence structure",
        "filler_count": 0,
        "start_time": 0,
        "end_time": 12,
        "duration": 12,
        "text_preview": "Welcome everyone to today's presentation..."
      },
      // ... more segments (variable count)
    ],
    "key_clips": {
      "good_clips": [
        {
          "segment_num": 3,
          "confidence": 92,
          "start_time": 28,
          "end_time": 35,
          "duration": 7,
          "text_preview": "This is an incredible opportunity...",
          "why_good": "✓ Perfect pace (150 WPM) | ✓ Minimal fillers (1) | ✓ Clear sentence structure",
          "title": "Strong Moment #3"
        }
      ],
      "bad_clips": [
        {
          "segment_num": 2,
          "confidence": 45,
          "start_time": 12,
          "end_time": 18,
          "duration": 6,
          "text_preview": "Unfortunately, um, we faced, like, some challenges...",
          "why_bad": "✗ Too many fillers (3, 12% of words) | ~ Pace: 140 WPM",
          "title": "Needs Work - Segment #2"
        }
      ],
      "explanation": "Found 1 strong moments and 1 moments that need improvement."
    }
  },
  "video_url": "/api/video/abc123"
}
```

---

## Success Criteria

✅ **All tests pass** → Ready to use!  
⚠️ **Some tests fail** → Debug specific issues  
❌ **Nothing works** → Check Docker logs and network tab

---

**Happy Testing! 🚀**
