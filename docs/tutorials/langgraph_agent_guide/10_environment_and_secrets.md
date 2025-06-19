# Best Practices for Environment and Execution

Building a great agent is only half the battle. Structuring your project correctly so it can be run reliably is just as important. This section covers two critical, non-obvious "gotchas" in Python development that frequently cause issues: loading secrets and running your code as a package.

## 1. Loading Secrets: The Execution Order Problem

When you initialize a LangChain component that needs an API key (like `ChatOpenAI`), the library reads the environment variable (e.g., `OPENAI_API_KEY`) at the moment the object is created in memory. This happens when the Python interpreter first executes the line `llm = ChatOpenAI(...)`.

A common mistake is to put your `load_dotenv()` call in your main application script (e.g., `main.py`). However, if your `main.py` imports your agent, and your agent file defines the LLM, the following happens:

1.  `python -m my_agent.main` starts.
2.  `main.py` begins importing `build_agent` from `agent.py`.
3.  The interpreter goes into `agent.py` to load its contents.
4.  It sees `llm = ChatOpenAI()` and tries to create the object. **It needs the API key now!**
5.  The `load_dotenv()` call back in `main.py` hasn't run yet, so the environment variable is missing. **The application crashes.**

### The Solution: Load Secrets First

To prevent this, you must load your environment variables *before any LangChain objects are initialized*. The best place to do this is at the **very top of your project's root `__init__.py` file.**

#### Example: `my_agent/__init__.py`

```python
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file in this directory.
# This MUST be the first thing to run so that any library that needs
# environment variables will have them available.
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Now, you can safely import your agent graph
from .agent import build_agent

graph = build_agent()
```

## 2. Running Your Agent: The Module Execution Problem

If your project code is split into multiple files and uses relative imports (e.g., `from .agent import ...`), you cannot run a single file as a script.

-   **Wrong:** `python my_agent/main.py`
-   **Error:** `ImportError: attempted relative import with no known parent package`

This happens because when you run a file directly, Python doesn't consider its parent folder to be a "package," so it doesn't know how to resolve the `.` in the import path.

### The Solution: Run as a Module

You must run your project as a module using the `-m` flag. This tells Python to treat your directory as a package, which correctly resolves the imports.

-   **Correct:** `python -m my_agent.main`

This command tells Python: "Find the `my_agent` package, and within it, run the `main.py` file as the script." This is the standard and correct way to execute packaged Python applications.

## 3. Dependency Management: `pyproject.toml` and Extras

To keep the core framework lightweight while providing powerful optional tools (like those for Google Workspace or Slack), we use a modern dependency management approach with `pyproject.toml`.

-   **Core Dependencies**: The main `[project.dependencies]` list contains only the essential packages required for any agent to run.
-   **Optional Extras**: Additional toolkits are defined under `[project.optional-dependencies]`. This allows a user to install support for a specific service without installing dozens of unrelated packages.

To install the core dependencies, run the following from the project root:
`pip install .`

To install an optional toolkit, use the "extra" syntax:
`pip install ".[gworkspace]"`
`pip install ".[slack]"`

This model provides a clean, professional, and non-intrusive way to manage dependencies. See the `14_core_tool_toolkit.md` guide for a full list of available toolkits. 