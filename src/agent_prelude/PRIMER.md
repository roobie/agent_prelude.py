# agent_prelude.py

> A prelude for your agent sessions to improve robustness 

## Agent Python: A Terse, Robust Prelude for LLM Agents

**Goal:** Let LLMs write Python that's as concise as Bash but inherently more robust, without magic syntax or custom DSLs.

### LLM Usage Examples

**Filesystem operations:**
```python
# Create directory and write JSON
mkdir('workspace/data')
write('workspace/config.json', {'api_key': 'abc123', 'enabled': True})

# Read and parse JSON automatically
config = read('workspace/config.json')

# List files
py_files = find('*.py')
log(f"Found {len(py_files)} Python files")

# Search across files
errors = grep('ERROR', 'logs/')
for err in errors:
    log(f"{err['file']}:{err['line']} - {err['text']}")
```

**HTTP operations:**
```python
# GET request, auto-parse JSON
users = get('https://api.example.com/users')
active_users = [u for u in users if u['status'] == 'active']

# POST with JSON
response = post('https://api.example.com/report', {'count': len(active_users)})

# Download file
download('https://example.com/data.csv', 'data/input.csv')
```

**Combined workflow:**
```python
# Fetch data
users = get('https://api.example.com/users')

# Filter and transform
active = [{'name': u['name'], 'email': u['email']} 
          for u in users if u['active']]

# Save results
mkdir('output')
write('output/active_users.json', active)
log(f"Saved {len(active)} active users")

# Search logs for issues
errors = grep('ERROR.*user', 'logs/', recursive=True)
if errors:
    write('output/errors.json', errors)
```

**Shell interop when needed:**
```python
# Use shell for complex operations
disk_usage = sh('df -h / | tail -1')
log(f"Disk usage: {disk_usage}")

# Or for tools not in the prelude
sh('git clone https://github.com/user/repo.git')
```

**Safer shell execution with `run()`:**
```python
# Use run() for commands with user input to avoid shell injection
# Instead of sh(f'grep "{pattern}" file.txt')
result = run(['grep', pattern, 'file.txt'])
log(f"Grep result: {result}")

# Check exit code
try:
    output = run(['git', 'status'], check=True)
    log("Git status successful")
except subprocess.CalledProcessError as e:
    log(f"Git command failed: {e}", level="ERROR")
```

**Advanced HTTP with raw response:**
```python
# Access full response object for headers/status
response = get('https://api.example.com/data', raw=True)
log(f"Status: {response.status_code}, Rate limit: {response.headers.get('X-RateLimit-Remaining')}")

# Conditional logic based on response
if response.status_code == 200:
    data = response.json()
    # Process data
```

**File operations with format control:**
```python
# Force JSON output even for strings
write('output/data.json', "some string data", format='json')

# Force text output for dicts
write('output/debug.txt', {'key': 'value'}, format='text')

# Append to log file
append('app.log', f"{now()}: Process started")
```

**Comprehensive scraping example (like HN points sum):**
```python
# Fetch HTML page
html = get('https://news.ycombinator.com/')

# Extract data with regex
import re
scores = re.findall(r'<span class="score"[^>]*>(\d+) points</span>', html)
total_points = sum(int(s) for s in scores)

# Log results
log(f"Total HN points: {total_points}", level="INFO")

# Save structured data
stories = []
for match in re.finditer(r'<a href="([^"]*)"[^>]*>([^<]*)</a>.*?<span class="score"[^>]*>(\d+) points</span>', html, re.DOTALL):
    stories.append({
        'url': match.group(1),
        'title': match.group(2),
        'points': int(match.group(3))
    })

write('hn_stories.json', stories)
log(f"Saved {len(stories)} stories")
```

**Error handling and logging:**
```python
try:
    data = get('https://api.example.com/data')
    log("Data fetched successfully")
except requests.HTTPError as e:
    log(f"HTTP error: {e}", level="ERROR")
except Exception as e:
    log(f"Unexpected error: {e}", level="ERROR")

# Use different log levels
log("Starting process", level="DEBUG")
log("Process completed", level="INFO")
log("Warning: low disk space", level="WARN")
```

**Working with paths and existence:**
```python
config_path = '~/myapp/config.json'
if not exists(config_path):
    write(config_path, {'default': True})

# List subdirectories
dirs = [d for d in ls('.') if os.path.isdir(d)]
log(f"Directories: {dirs}")

# Find specific files recursively
test_files = find('test_*.py', 'src/')
log(f"Found {len(test_files)} test files")
```

---

### Key Design Principles

**1. Sensible defaults, explicit overrides:**
```python
data = read('file.json')  # Auto-detects JSON
data = read('file.txt', format='text')  # Explicit when needed
```

**2. Auto-create parents, never fail on "already exists":**
```python
mkdir('deep/nested/path')  # Just works
write('new/dir/file.txt', 'data')  # Creates dirs automatically
```

**3. Return structured data by default:**
```python
errors = grep('ERROR', 'logs/')  # Returns list of dicts, not text
# [{'file': 'app.log', 'line': 42, 'text': 'ERROR: failed'}]
```

**4. Paths are always strings (no Path object leakage):**
```python
files = find('*.py')  # Returns list of strings
for f in files:
    content = read(f)  # Takes strings
```

**5. Errors are explicit (raise exceptions):**
```python
data = get('https://api.example.com/data')  # Raises on HTTP error
# LLM can wrap in try/except if needed
```

---

### What This Gives You

**Terseness:**
- No imports
- No boilerplate (mkdir parents, JSON parsing, etc.)
- Single-word function names for common operations

**Robustness:**
- Timeouts on HTTP by default
- Proper error handling (exceptions, not silent failures)
- Path expansion (~/ works)
- Auto-create directories

**Familiarity:**
- Function names match Unix tools (ls, find, grep, mkdir)
- Still recognizable as Python
- No custom syntax or operators

**Flexibility:**
- Explicit parameters when you need control
- Shell escape hatch with `sh()` for anything else
- Standard Python for complex logic

---

### Implementation Notes

**The prelude is ~150 lines** — small enough to understand, large enough to be useful.

**Auto-injection options:**
```bash
# Option 1: Wrapper script
agent-python script.py  # Prepends prelude automatically

# Option 2: PYTHONSTARTUP
export PYTHONSTARTUP=~/.agent_prelude.py

# Option 3: Explicit import
from agent_prelude import *  # LLM includes this line
```

**Extensions can be added without breaking terseness:**
```python
# Cache decorator for expensive operations
@cache(ttl=3600)
def get(url, **kwargs):
    # ... existing implementation

# Retry decorator for flaky operations  
@retry(times=3, backoff=2)
def get(url, **kwargs):
    # ... existing implementation
```

The LLM still writes `get(url)`, but gets caching and retries automatically.

---

### Why This Works

**It's just Python** — debuggable, portable, no magic.

**It matches LLM intuition** — function names are obvious, behavior is predictable.

**It's incrementally adoptable** — start with the prelude, add runtime features (caching, logging, transactions) later without changing LLM code.

**It scales** — simple scripts stay simple, complex logic is still full Python.

