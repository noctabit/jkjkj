const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

// Configure Express to trust proxy (required for Replit environment)
app.set('trust proxy', true);

// Serve static files
app.use(express.static('public'));

// Parse SRT file function
function parseSRT(content) {
  const subtitles = [];
  const blocks = content.trim().split(/\n\s*\n/);
  
  for (const block of blocks) {
    const lines = block.trim().split('\n');
    if (lines.length >= 3) {
      const index = parseInt(lines[0]);
      const timeRange = lines[1];
      const text = lines.slice(2).join(' ');
      
      if (!isNaN(index) && timeRange.includes('-->')) {
        subtitles.push({
          index,
          timeRange,
          text
        });
      }
    }
  }
  
  return subtitles;
}

// Main route
app.get('/', (req, res) => {
  try {
    const srtContent = fs.readFileSync('en.srt', 'utf8');
    const subtitles = parseSRT(srtContent);
    
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subtitle Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .subtitle-item {
            background-color: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .subtitle-index {
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }
        .subtitle-time {
            color: #888;
            font-size: 0.85em;
            margin: 5px 0;
        }
        .subtitle-text {
            font-size: 1.1em;
            line-height: 1.4;
            color: #333;
        }
        .stats {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #e9e9e9;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Subtitle Viewer</h1>
        <p>Documentary Subtitles</p>
    </div>
    
    <div class="stats">
        <strong>Total Subtitles: ${subtitles.length}</strong>
    </div>
    
    <div class="subtitles">
        ${subtitles.map(sub => `
            <div class="subtitle-item">
                <div class="subtitle-index">#${sub.index}</div>
                <div class="subtitle-time">${sub.timeRange}</div>
                <div class="subtitle-text">${sub.text}</div>
            </div>
        `).join('')}
    </div>
</body>
</html>`;
    
    res.send(html);
  } catch (error) {
    res.status(500).send(`
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
    <h1>Error loading subtitles</h1>
    <p>${error.message}</p>
</body>
</html>`);
  }
});

// API endpoint to get subtitles as JSON
app.get('/api/subtitles', (req, res) => {
  try {
    const srtContent = fs.readFileSync('en.srt', 'utf8');
    const subtitles = parseSRT(srtContent);
    res.json(subtitles);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Subtitle viewer running on http://0.0.0.0:${PORT}`);
  console.log(`Ready to display subtitle content!`);
});