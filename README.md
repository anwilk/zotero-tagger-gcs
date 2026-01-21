# Literature Abstract Tagging

This project provides a graphical user interface (GUI) to help assign metadata tags to literature abstracts. It uses the Zotero API to fetch abstracts and the Google Gemini API to provide AI-powered tagging suggestions, which can then be reviewed and confirmed by the user.

## Running the Application

Below are the step-by-step instructions for running the application on both a local device and Google Cloud Shell.

---

### 1. Prerequisites

Before you begin, ensure you have the following:

*   **Python 3.8+**: To check if you have Python installed, open a terminal or command prompt and run `python3 --version`.
*   **Zotero Account**: With your literature stored in a library.
*   **Google Account**: To access the Gemini API.
*   The metadata dictionary file named `metadata_Dictionary_v2.csv` in the `data/` directory.

---

### 2. Setup and Configuration

#### On a Local Device (Windows, macOS, Linux)

1.  **Clone the Repository**:
    Open a terminal and clone the project files to your local machine:
    ```bash
    git clone <repository_url>
    cd zotero-tagger-gcs
    ```
    (Replace `<repository_url>` with the actual URL of your repository.)

2.  **Install Dependencies**:
    Install the required Python libraries using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

#### On Google Cloud Shell

1.  **Launch Cloud Shell**:
    Open the [Google Cloud Console](https://console.cloud.google.com/) and click the "Activate Cloud Shell" button in the top-right corner.

2.  **Upload Project Files**:
    *   If you have the project as a `.zip` file, click the three-dot menu in Cloud Shell, select "Upload File," and upload your project. Then, unzip it using the `unzip` command.
    *   Alternatively, you can clone the repository directly into your Cloud Shell environment as described in the local setup.

3.  **Install Dependencies**:
    Cloud Shell comes with Python and pip pre-installed. Navigate to your project directory and run:
    ```bash
    cd lit-tagging
    pip install -r requirements.txt --user
    ```
    You will also need to upload your `metadata_Dictionary_v2.csv` file into the `data/` directory using the "Upload File" option.

---

### 3. API Key Configuration

This is a critical step for the application to function correctly.

1.  **Locate the Configuration File**:
    Find the `config.ini` file in the main project directory.

2.  **Add Your Zotero API Credentials**:
    *   Open `config.ini` in a text editor.
    *   Replace `YOUR_LIBRARY_ID` with your Zotero User or Group ID. You can find this by going to `zotero.org`, navigating to your library or group, and looking at the URL (e.g., `zotero.org/users/<library_id>/...`).
    *   Replace `YOUR_API_KEY` with a new private key from the [Zotero Feeds/API settings page](https://www.zotero.org/settings/keys).

3.  **Add Your Google AI API Key**:
    *   In the same `config.ini` file, find the `[gemini]` section.
    *   Replace `YOUR_GEMINI_API_KEY` with your Google AI API key. You can generate one at [Google AI Studio](https://makersuite.google.com/app/apikey).

---

### 4. Running the Application

The application runs in two stages: fetching the abstracts, then tagging them.

1.  **Fetch Abstracts from Zotero**:
    First, run the fetch script from your terminal. This will connect to your Zotero library and download all items that have an abstract.
    ```bash
    python3 scripts/fetch_abstracts.py
    ```
    This will create a `zotero_items.json` file in the `data/` directory.

2.  **Launch the Tagging GUI**:
    Once the abstracts are fetched, start the graphical tagging interface:
    ```bash
    python3 scripts/tag_abstracts.py
    ```
    The GUI will launch, displaying the first abstract and the tagging options.

### How to Use the GUI

*   **Get AI Suggestions**: Click this button to have the Gemini AI suggest tags for the current abstract based on the tag definitions from `data/metadata_Dictionary_v2.csv`. The corresponding checkboxes will be checked.
*   **Review and Edit**: Manually check or uncheck boxes to correct the tags.
*   **Save & Next**: Saves the currently selected tags and moves to the next abstract. Your work is saved to `data/tagged_items.json`.
*   **Skip**: Moves to the next abstract without saving any tags for the current one.
