# RedNote Scraping Task

A lightweight Python command-line tool for collecting public Xiaohongshu (RedNote) search results. It opens a real Chromium browser, listens for the search data loaded by the page, and exports the available post metadata to CSV.

> This project does not bypass authentication, CAPTCHAs, access controls, or platform rate limits. Only collect public content that you are authorized to access, and comply with Xiaohongshu's terms of service, robots rules, and applicable laws.

## Features

- Collect public search results by keyword
- Configure the result limit, output path, and timeout values
- Export titles, captions, authors, engagement counts, publication times, and media URLs
- Deduplicate results and skip records without an author
- Preserve available search metadata when a post detail page cannot be loaded
- Write UTF-8 CSV files with a byte order mark for reliable Chinese text display in Excel

## Project Structure

```text
rednote-scraping-task/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── collect_xhs.py
└── LICENSE
```

## Requirements

- Python 3.10 or later
- Git, unless you download the repository as a ZIP archive
- Google Chrome, Chromium, or another Chromium-based browser supported by DrissionPage
- Network access to the Xiaohongshu website

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/LehanDong/rednote-scraping-task.git
cd rednote-scraping-task

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On Windows PowerShell, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Usage

Collect up to 100 results for the keyword `Shanghai coffee`:

```bash
python3 src/collect_xhs.py --keyword "Shanghai coffee" --limit 100
```

The default output file is `output/search_results.csv`, relative to the directory from which you run the command. An existing file at the same path will be overwritten. To choose another path:

```bash
python3 src/collect_xhs.py \
  --keyword "Shanghai coffee" \
  --limit 50 \
  --output output/shanghai_coffee.csv
```

The script opens a browser window and begins waiting for search results immediately. If Xiaohongshu asks you to sign in, complete the sign-in manually in that window. The script does not store usernames or passwords. CAPTCHAs must also be handled manually and should never be bypassed.

By default, the script stops after three consecutive rounds without new data. If sign-in takes too long and the script exits, run it again after signing in or increase `--listen-timeout` and `--max-idle-rounds`.

### Command-Line Options

| Option | Short form | Default | Description |
| --- | --- | --- | --- |
| `--keyword` | `-k` | Required | Search keyword |
| `--limit` | `-n` | `100` | Maximum number of valid records to save |
| `--output` | `-o` | `output/search_results.csv` | CSV output path |
| `--scroll-delay` |  | `2` | Seconds to wait after each page scroll |
| `--listen-timeout` |  | `15` | Seconds to wait for a search API response |
| `--request-timeout` |  | `15` | Timeout in seconds for each post detail request |
| `--max-idle-rounds` |  | `3` | Stop after this many consecutive rounds without new data |

Display the complete command-line help:

```bash
python3 src/collect_xhs.py --help
```

## CSV Columns

| Column | Description |
| --- | --- |
| `Post URL` | URL of the post |
| `Author Name` | Author's display name |
| `Likes` | Like count as returned by the platform |
| `Comments` | Comment count as returned by the platform |
| `Post Title` | Post title |
| `Caption` | Post caption or page description |
| `Date Published` | Publication time in the computer's local time zone |
| `Video URL` | Video URLs separated by semicolons |
| `User URL` | Author profile URL |
| `Images URL` | Image URLs separated by semicolons |

## Troubleshooting

### The script repeatedly reports that no new data was received

Make sure the browser page loaded successfully, your network connection is working, and you have signed in if the website requires it. You can also increase `--listen-timeout`.

### Fewer records are saved than requested

The available search results may have been exhausted, may contain duplicates, or may include incomplete records. Login or CAPTCHA delays and individual record-processing errors can also reduce the final count. After several rounds without new data, the script stops safely and keeps the records already written to the CSV file.

### Captions, publication times, or media URLs are missing

Xiaohongshu may change its page structure or response fields, and different post types expose different metadata. The script preserves all fields it can still read from the search response.

## Responsible Use

- Use this project only for learning, research, or other authorized data-processing activities.
- Do not collect private, sensitive, or otherwise unauthorized data.
- Do not circumvent sign-in requirements, CAPTCHAs, access controls, rate limits, or other security measures.
- Keep request rates low and anonymize data when appropriate before publishing it.
- You are responsible for ensuring that your use complies with platform rules and applicable laws.

## License

This project is licensed under the [MIT License](LICENSE).
