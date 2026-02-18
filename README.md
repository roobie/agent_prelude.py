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
