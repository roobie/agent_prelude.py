# Essential Patterns and Anti-Patterns for Coding Agents

> NOTE (operational requirement): Any and all agent actions MUST be recorded as a chronicle entry.  
> Create or append a markdown file under the repository `chronicles/` directory for each session or significant action. Each chronicle entry should include: timestamp, participants, summary of actions taken, commands run (representative), files added/modified, and suggested next steps. Keep chronicles up to date — they are the authoritative historical record of agent activity.

Here are the **most critical patterns for building robust, secure software**, prioritized for coding agents to follow:

---

## 1. Parse, Don't Validate

**Parse inputs into structured, type-safe data at boundaries. Don't just check validity and pass raw data forward.**

- Transform untrusted input into types that make invalid states impossible
- Validate once at the boundary, then trust your types internally
- **Security impact:** Prevents injection attacks, data corruption, and logic errors from malformed input

---

## 2. Principle of Least Privilege

**Grant the minimum permissions necessary for code to function. No more, no less.**

- Run processes with minimal user privileges
- Limit database user permissions to only required operations
- Use read-only file system access when writes aren't needed
- Scope API tokens and credentials as narrowly as possible
- **Security impact:** Limits blast radius of vulnerabilities and compromised components

---

## 3. Fail Securely (Secure Defaults)

**When errors occur, fail in a way that maintains security. Default to the most restrictive option.**

- On authentication failure, deny access (don't fall back to permissive mode)
- On parsing errors, reject the input (don't guess or auto-correct)
- On configuration errors, use secure defaults (not convenient ones)
- Log failures but don't expose sensitive details in error messages
- **Security impact:** Prevents attackers from exploiting error conditions to bypass security

---

## 4. Defense in Depth

**Layer multiple independent security controls. Never rely on a single protection mechanism.**

- Validate input at UI, API, and database layers
- Use authentication AND authorization AND rate limiting
- Combine parameterized queries with input validation
- Apply encryption in transit AND at rest
- **Security impact:** If one layer fails, others still provide protection

---

## 5. Make Illegal States Unrepresentable

**Design data structures so invalid states cannot be constructed.**

**Bad:**
```typescript
interface Connection {
  isConnected: boolean;
  socket: Socket | null;
  error: Error | null;
}
// Can create invalid states: isConnected=true but socket=null
```

**Good:**
```typescript
type Connection = 
  | { status: 'connected'; socket: Socket }
  | { status: 'disconnected' }
  | { status: 'error'; error: Error };
// Invalid states are impossible
```

- **Robustness impact:** Eliminates entire classes of bugs at compile time
- **Security impact:** Prevents logic errors that could bypass security checks

---

## 6. Avoid Midlayer Mistakes

**Provide libraries of optional helper functions. Don't create forced abstraction layers.**

- Build rich, flexible interfaces at lower levels
- Offer helper functions that can be used optionally
- Don't force all code through a common abstraction that makes assumptions
- **Robustness impact:** Prevents brittle architectures that break when requirements evolve

---

## 7. Explicit Resource Management

**Always clean up resources (files, connections, memory) even when errors occur.**

**Bad:**
```typescript
const file = openFile('data.txt');
processFile(file); // If this throws, file never closes
file.close();
```

**Good:**
```typescript
const file = openFile('data.txt');
try {
  processFile(file);
} finally {
  file.close();
}
// Or use RAII/with-statements/using declarations
```

- Use try-finally, defer, RAII, or language-specific resource management
- Never leave connections open, files unlocked, or memory leaked
- **Robustness impact:** Prevents resource exhaustion and deadlocks
- **Security impact:** Prevents DoS through resource exhaustion

---

## 8. Sanitize Outputs, Not Just Inputs

**Encode/escape data appropriately for its output context.**

- HTML-encode for HTML contexts
- SQL-parameterize for database queries
- Shell-escape for command execution
- JSON-encode for JSON contexts
- URL-encode for URLs
- **Security impact:** Prevents XSS, SQL injection, command injection, and other injection attacks

---

## 9. Avoid Primitive Obsession

**Use domain types instead of primitives (strings, numbers, booleans) for important concepts.**

**Bad:**
```typescript
function transferMoney(amount: number, fromAccount: string, toAccount: string)
```

**Good:**
```typescript
type Money = number & { readonly __brand: 'Money' };
type AccountId = string & { readonly __brand: 'AccountId' };
function transferMoney(amount: Money, from: AccountId, to: AccountId)
```

- Prevents passing arguments in wrong order
- Makes units and constraints explicit
- Enables type system to catch errors
- **Robustness impact:** Catches bugs at compile time
- **Security impact:** Prevents logic errors in critical operations

---

## 10. Immutability by Default

**Make data structures immutable unless mutation is explicitly needed.**

- Use `const`, `readonly`, `final`, or language-specific immutability features
- Return new objects instead of modifying existing ones
- **Robustness impact:** Eliminates race conditions and unexpected state changes
- **Security impact:** Prevents time-of-check-time-of-use (TOCTOU) vulnerabilities

---

## Anti-Patterns to Avoid

### Security by Obscurity
- **Don't** rely on keeping implementation details secret
- **Do** assume attackers know your system architecture
- Use proper cryptography, authentication, and authorization

### Rolling Your Own Crypto
- **Don't** implement your own encryption, hashing, or random number generation
- **Do** use well-tested, standard libraries (libsodium, OpenSSL, platform crypto APIs)

### Trusting Client-Side Validation
- **Don't** rely on JavaScript validation or client-side checks for security
- **Do** always validate on the server, treating all client input as untrusted

### String Concatenation for Queries
- **Don't** build SQL, HTML, or shell commands by concatenating strings
- **Do** use parameterized queries, template engines with auto-escaping, or safe APIs

### Logging Sensitive Data
- **Don't** log passwords, tokens, credit cards, or PII
- **Do** redact sensitive fields before logging

---

# CTAGS

## Instructions for LLM Coding Agent: Using ctags Tags File

**The `tags` file is a sorted index of code symbols (functions, classes, variables, etc.) with their locations.**

---

### File Format

Each line in the `tags` file follows this structure:
```
<symbol_name><TAB><file_path><TAB><search_pattern_or_line_number>;<metadata>
```

Example:
```
MyComponent	src/components/MyComponent.tsx	/^export function MyComponent() {$/;" 	f
useState	src/hooks/useAuth.ts	25;" 	v
```

---

### How to Use

**1. Find symbol definitions:**
```bash
grep "^symbolName\t" tags
```

**2. Extract file path and location:**
Parse the tab-separated fields:
- Field 1: Symbol name
- Field 2: File path (relative to project root)
- Field 3: Search pattern (between `/^` and `$/`) or line number

**3. Navigate to definition:**
- Open the file from field 2
- Use the regex pattern from field 3 to locate the exact line, OR
- Jump to the line number if provided

**4. For faster lookups** (tags file is sorted):
```bash
look symbolName tags
```

---

### Practical Workflow

When asked to find, modify, or understand code:

1. **Search tags**: `grep "^functionName\t" tags`
2. **Parse result**: Extract file path and location
3. **Read file**: Open and read the relevant file section
4. **Provide answer**: Use the code context to respond accurately

---

### Example Usage

**User asks**: "Where is the `UserProfile` component defined?"

**Agent action**:
```bash
grep "^UserProfile\t" tags
# Result: UserProfile	src/components/UserProfile.tsx	/^export const UserProfile = () => {$/;" 	C
```

**Agent response**: "The `UserProfile` component is defined in `src/components/UserProfile.tsx`" (then read that file for details)

---

### Key Benefits

- **Fast symbol lookup** without reading entire codebase
- **Accurate file locations** for definitions
- **Efficient navigation** in large projects
- **Works offline** - no API calls needed


# `agh` (Agent Harness) Primer for LLMs

`agh` is a command-line tool that executes Python code with a rich set of utility functions pre-loaded from `agent_prelude.py`. It allows you to perform file operations, HTTP requests, shell commands, logging, and more, all within Python scripts piped via stdin.

## Why Prefer `agh` Over Bash?

- **Power and Flexibility**: Python's full syntax and libraries for complex logic, data processing, error handling, and automation.
- **Safety**: Better handling of special characters, structured data (JSON), and cross-platform compatibility.
- **Consistency**: Use the same language for scripting and application logic.
- **Pre-loaded Utilities**: Immediate access to common operations without imports or setup.
- **Integration**: Easily combine file ops, HTTP calls, and shell commands in one script.

## Installation

Run: `agh --install` (symlinks to ~/.local/bin/agh)

## Usage

Pipe Python code to `agh`:

```bash
agh <<EOF
# Your Python code here
print("Hello World")
EOF
```

Or via pipe: `echo 'print("Hello")' | agh`

## Available Functions from agent_prelude.py

### Filesystem Operations

- `read(path, format="auto")`: Read file as text or JSON (auto-detects .json).
- `write(path, data, format="auto")`: Write data to file, auto-serializing dicts/lists to JSON.
- `append(path, data)`: Append string to file.
- `exists(path)`: Check if path exists.
- `ls(path=".", pattern="*")`: List files matching glob pattern.
- `find(pattern, path=".")`: Recursively find files matching pattern.
- `mkdir(path)`: Create directory and parents.
- `grep(pattern, path, recursive=True)`: Search for regex pattern in files, returns list of matches.

### HTTP Operations

- `get(url, timeout=30, raw=False, **kwargs)`: HTTP GET, returns JSON or text.
- `post(url, data=None, timeout=30, raw=False, **kwargs)`: HTTP POST with JSON data.
- `download(url, path, timeout=30)`: Download file from URL to path.

### Shell Interop

- `sh(command, check=False)`: Run shell command, return stdout (optionally check exit code).
- `run(args, check=False)`: Run command with args list, return stdout.

### Utilities

- `log(msg, level="INFO")`: Log message to stderr with timestamp (levels: DEBUG, INFO, WARN, ERROR).
- `now()`: Return current datetime object.

### Imported Modules

All standard imports from agent_prelude.py are available:
- `sys`, `os`, `re`, `json`, `Path` (from pathlib), `datetime`, `timedelta`, `subprocess`, `requests`

## Examples

### File Operations
```python
# Read and write JSON
data = read("config.json")
data["new_key"] = "value"
write("config.json", data)

# Find and process files
for f in find("*.py"):
    content = read(f)
    if "TODO" in content:
        log(f"TODO found in {f}")
```

### HTTP Requests
```python
# Fetch API data
response = get("https://api.github.com/user", headers={"Authorization": "token ..."})
print(response["login"])

# Download file
download("https://example.com/file.zip", "/tmp/file.zip")
```

### Shell Integration
```python
# Run commands
output = sh("ls -la")
files = output.split("\n")

# Safe command execution
try:
    result = sh("git status", check=True)
    print(result)
except Exception as e:
    log(f"Git command failed: {e}", "ERROR")
```

### Complex Tasks
```python
# Backup files with logging
import shutil

log("Starting backup")
for f in find("*.txt"):
    backup = f + ".bak"
    shutil.copy(f, backup)
    log(f"Backed up {f}")

# Process CSV-like data
lines = read("data.txt").split("\n")
processed = [line.upper() for line in lines if line.strip()]
write("processed.txt", "\n".join(processed))
```

## Best Practices

- Use `log()` for debugging and status messages.
- Handle exceptions with try/except for robustness.
- Combine functions for powerful scripts (e.g., read config, make HTTP calls, update files).
- Prefer `run()` for commands with arguments to avoid shell injection.
- Use `Path` for cross-platform path handling.

## Common Patterns

- **Data Processing**: Read files, manipulate in Python, write back.
- **Automation**: Chain HTTP requests, file ops, and shell commands.
- **Error Handling**: Use try/except, log errors.
- **Configuration**: Store settings in JSON, load with `read()`.

This primer equips you to leverage `agh` for efficient, powerful scripting over bash.
