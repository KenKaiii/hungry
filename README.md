# Hungry Crawler

A powerful web crawler and scraper with a terminal-based UI for extracting and analyzing web content.


> [!TIP]
> **Want to build your own apps with AI?** A free 7-day build challenge and 20+ step-by-step projects are in my free community: **[skool.com/raid](https://www.skool.com/raid)**

## 🚀 Features

- **Web Crawling**: Discover and map all pages on a website
- **Web Scraping**: Extract content from specific pages
- **Multiple Export Formats**: Convert to Markdown, JSON, HTML, or CSV
- **Batch Processing**: Scrape multiple URLs from previous crawls
- **Pause & Resume**: Save crawl state and resume later
- **Content Search**: Find specific content in your crawled/scraped data
- **Proxy Support**: Use proxies to avoid IP blocking
- **User Agent Rotation**: Rotate user agents to appear more like a regular browser
- **Robots.txt Compliance**: Respect website crawling rules
- **Rate Limiting**: Configurable delays between requests
- **Blacklist/Whitelist**: Control which URLs are crawled

## 📋 Requirements

- Python 3.6+
- Windows or macOS/Linux

## 🔧 Installation

1. Clone this repository:

   Make a new folder
   Open up your terminal / Powershell
   Navigate to the folder
   ```
   cd "name of folder"
   ```
   Once you're in that folder, use the "git clone" command below.
   ```
   git clone https://github.com/KenKaiii/hungry.git
   ```
   Now navigate to that folder that was downloaded
   ```
   cd hungry
   ```

3. Run the setup script:

   **Windows:**
   ```
   .\setup.bat
   ```

   **macOS/Linux:**
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

4. The setup script will:
   - Create a virtual environment
   - Install required dependencies
   - Set up necessary folders
   - Create default settings

## 🖥️ Usage

Run the crawler:

**Windows:**
```
.\hungry.bat
```

**macOS/Linux:**
```
./hungry.sh
```

Get help:

**Windows:**
```
hungry.bat /help
```

**macOS/Linux:**
```
./hungry.sh --help
```

### Main Operations:

1. **Crawl**: Discover all pages on a website
2. **Scrape**: Extract content from a specific page
3. **Scrape All URLs**: Process multiple URLs from a previous crawl
4. **Resume Crawl**: Continue a previously paused crawl
5. **Search**: Find content in your crawled/scraped data
6. **Settings**: Configure crawler behavior

## 📁 Folder Structure

- **Results/**: Contains scraped content
- **Crawled/**: Contains lists of crawled URLs
- **Exports/**: Contains exported data
- **Logs/**: Contains log files

## ⚙️ Configuration

You can configure the crawler through the Settings menu or by directly editing the `settings.json` file.

Key settings:
- `respect_robots_txt`: Whether to respect robots.txt rules
- `crawl_delay`: Delay between requests in seconds
- `max_pages`: Maximum number of pages to crawl before asking to continue
- `export_formats`: Default export formats
- `use_proxies`: Whether to use proxies
- `proxies`: List of proxy URLs to use
- `rotate_user_agents`: Whether to rotate user agents

## ⚠️ Legal Disclaimer

This tool is provided for educational and research purposes only. Always respect website terms of service and robots.txt rules. The authors are not responsible for any misuse of this software.

## 📄 License

MIT License

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Credits

Created by KenKaiii
