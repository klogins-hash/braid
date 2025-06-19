# 14. Core Tool Toolkit

Our framework includes a powerful set of pre-built tools for common integrations, located in the `core/contrib/` directory. This "batteries-included" approach allows agents to easily interact with external services like Google Workspace, Slack, and Microsoft 365.

To keep the core framework lightweight, the dependencies for these tools are **optional**. You only need to install the packages for the tools you intend to use.

---

### The "Extras" Installation Model

Dependencies are managed in `pyproject.toml` under the `[project.optional-dependencies]` section. Each key (e.g., `gworkspace`, `slack`) defines an "extra."

To install the dependencies for a specific toolkit, you use the following `pip` command from your project root:

```bash
# General format
pip install ".[<extra_name>]"

# Example for Google Workspace tools
pip install ".[gworkspace]"

# Example for Slack tools
pip install ".[slack]"
```

If you try to use a tool without installing its dependencies, the framework will raise a helpful `ImportError` telling you exactly which command to run.

---

### Available Toolkits

#### 1. Google Workspace (`gworkspace`)

-   **Installation**: `pip install ".[gworkspace]"`
-   **Setup**:
    1.  Go to the Google Cloud Console, create a project, and enable the relevant APIs (e.g., Google Calendar API, Gmail API).
    2.  Create **OAuth 2.0 Credentials** for a **Desktop App**.
    3.  Download the credentials JSON file and save it as `credentials/google_credentials.json`.
    4.  The first time an agent uses a Google tool, it will open a browser for you to authorize the application. This creates a `credentials/google_token.json` file for future, non-interactive use.

-   **Tools Provided**:
    -   `create_google_calendar_event`: Creates a new event on the user's primary calendar.
    -   `gmail_send_email`: Sends an email from the user's Gmail account.
    -   `gsheets_append_row`: Appends a row of data to a specified Google Sheet.

#### 2. Slack (`slack`)

-   **Installation**: `pip install ".[slack]"`
-   **Setup**:
    1.  Create a Slack App in your workspace.
    2.  Add the required Bot Token Scopes (e.g., `chat:write`, `files:write`).
    3.  Install the app to your workspace and get the **Bot User OAuth Token**.
    4.  Set this token as an environment variable named `SLACK_BOT_TOKEN` in your agent's `.env` file.

-   **Tools Provided**:
    -   `slack_post_message`: Sends a message to a Slack channel or user.
    -   `slack_upload_file`: Uploads a file from a local path to a Slack channel.

#### 3. Microsoft 365 (`ms365`)

-   **Installation**: `pip install ".[ms365]"`
-   **Setup**:
    1.  Register an application in the Microsoft Entra admin center.
    2.  Grant it the necessary delegated permissions from Microsoft Graph (e.g., `User.Read`, `Mail.Send`, `ChannelMessage.Send`).
    3.  Create a client secret for the application.
    4.  Create a file at `credentials/ms365_credentials.json` containing your application's `client_id` and `client_secret`.
    5.  Similar to Google, the first use will trigger a browser-based authentication flow to get a user token.

-   **Tools Provided**:
    -   `teams_post_message`: Sends a message to a specific channel in Microsoft Teams.
    -   `outlook_send_email`: Sends an email from the user's Outlook account.
    -   `graph_get_user`: Fetches the profile of the authenticated user. 