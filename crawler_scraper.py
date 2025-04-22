import os
import sys
import time
import json
import requests
import argparse
import markdown
import random
import re
import unicodedata
import logging
import csv
import signal
import itertools
import threading
import io
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from rich.syntax import Syntax
from rich import box
import pyfiglet

# Initialize Rich console with a wider width for better visuals
console = Console(width=100, highlight=True)

# Define color gradients for a cyberpunk look
GRADIENT_COLORS = [
    "bright_blue", "blue", "cyan", "bright_cyan", "green", "bright_green", 
    "yellow", "bright_yellow", "red", "bright_red", "magenta", "bright_magenta"
]

def gradient_text(text, start_color="bright_blue", end_color="bright_green"):
    """Create a gradient effect for text"""
    if start_color == end_color:
        return f"[{start_color}]{text}[/{start_color}]"
    
    # Get the indices of the gradient colors
    start_idx = GRADIENT_COLORS.index(start_color)
    end_idx = GRADIENT_COLORS.index(end_color)
    
    # Determine the direction of the gradient
    step = 1 if start_idx < end_idx else -1
    colors = GRADIENT_COLORS[start_idx:end_idx+step:step] if step > 0 else GRADIENT_COLORS[start_idx:end_idx+step:step]
    
    # If we don't have enough colors, repeat them
    if len(colors) < len(text):
        colors = list(itertools.islice(itertools.cycle(colors), len(text)))
    
    # If we have too many colors, truncate them
    if len(colors) > len(text):
        colors = colors[:len(text)]
    
    # Create the gradient text
    result = ""
    for char, color in zip(text, colors):
        result += f"[{color}]{char}[/{color}]"
    
    return result

def typing_effect(text, delay=0.01):
    """Create a typing effect for text"""
    for char in text:
        console.print(char, end="", highlight=False)
        time.sleep(delay)
    console.print()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hungry_crawler")

# Version information
VERSION = "1.0.0"

# Default settings
DEFAULT_SETTINGS = {
    "respect_robots_txt": True,
    "crawl_delay": 2,
    "max_pages": 100,
    "timeout": 15,
    "max_retries": 3,
    "user_agent": "HungryCrawler/1.0",
    "blacklist": [],
    "whitelist": [],
    "export_formats": ["json", "csv", "txt"],
    "use_proxies": False,
    "proxies": [],
    "rotate_user_agents": True,
    "save_crawl_state": True
}

# Load settings or create default
def load_settings():
    """Load settings from settings.json or create with defaults"""
    settings_file = Path("settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Update with any missing default settings
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS
    else:
        # Create default settings file
        with open(settings_file, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4, sort_keys=True)
        return DEFAULT_SETTINGS

# Global settings
SETTINGS = load_settings()

def display_boot_sequence():
    """Display a simplified boot sequence"""
    console.clear()
    
    # Simple boot message with consistent colors
    console.print("[cyan]HUNGRY CRAWLER[/cyan]")
    console.print("[green]Initializing system...[/green]")
    
    # Simple progress bar with consistent colors
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[green]Loading...[/green]"),
        BarColumn(complete_style="cyan"),
        console=console
    ) as progress:
        task = progress.add_task("Loading", total=100)
        for _ in range(10):
            progress.update(task, advance=10)
            time.sleep(0.1)
    
    console.print("[green]System ready![/green]")
    time.sleep(0.5)
    console.clear()

def display_banner():
    """Display ASCII art banner from file"""
    # Display simplified boot sequence
    display_boot_sequence()
    
    # Read ASCII art from file
    try:
        with open("ascii.md", "r", encoding="utf-8") as f:
            banner_text = f.read()
            # Ensure we have content
            if not banner_text.strip():
                raise FileNotFoundError("ASCII art file is empty")
    except Exception as e:
        # Log the error
        logger.error(f"Error reading ASCII art: {e}")
        # Fallback if file can't be read
        banner_text = pyfiglet.figlet_format("HUNGRY CRAWLER", font="slant")
    
    # Create a simple colored banner with consistent colors
    console.print(Panel(
        f"[cyan]{banner_text}[/cyan]",
        subtitle="[green]CRAWL & SCRAPE THE WEB[/green]",
        border_style="cyan",
        box=box.DOUBLE_EDGE
    ))
    
    # Add version and creator info
    console.print(f"\n[dim]Created by: KenKaiii | Version: {VERSION}[/dim]\n")

def display_exit_animation():
    """Display a simplified exit animation"""
    try:
        console.clear()
        
        # Simple exit message with consistent colors
        console.print("[cyan]Exiting Hungry Crawler...[/cyan]")
        
        # Simple progress bar with consistent colors
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[green]Shutting down...[/green]"),
            BarColumn(complete_style="cyan"),
            console=console
        ) as progress:
            task = progress.add_task("Exiting", total=100)
            for _ in range(10):
                progress.update(task, advance=10)
                time.sleep(0.1)
        
        # Final exit message with consistent colors
        console.clear()
        exit_text = pyfiglet.figlet_format("GOODBYE", font="slant")
        console.print(f"[cyan]{exit_text}[/cyan]")
        console.print("[green]Thanks for using Hungry Crawler![/green]")
        
        time.sleep(0.5)
    except KeyboardInterrupt:
        # If user interrupts during exit animation, just exit silently
        pass
    except Exception:
        # For any other exception, just continue with exit
        pass
    
    # Force exit without any further processing
    os._exit(0)

def display_help():
    """Display help information about crawling and scraping"""
    console.clear()
    
    # Display a cool "HELP SYSTEM" banner
    help_banner = pyfiglet.figlet_format("HELP SYSTEM", font="banner3-D")
    console.print(f"[bold cyan]{help_banner}[/bold cyan]")
    
    # Create a more visually appealing help layout
    layout = Layout()
    layout.split_column(
        Layout(name="title"),
        Layout(name="content", ratio=8)
    )
    
    # Title section
    layout["title"].update(Panel(
        Align.center(gradient_text("HUNGRY CRAWLER DOCUMENTATION", "bright_cyan", "bright_green")),
        border_style="cyan",
        box=box.HEAVY_EDGE
    ))
    
    help_text = """
# HUNGRY CRAWLER - HELP

## What is Web Crawling?
Web crawling is the process of automatically navigating through websites and discovering links to other pages. 
A crawler (or spider) starts at a seed URL and follows links to find more pages, building a map of the web.

## What is Web Scraping?
Web scraping is the extraction of specific data from websites. It involves parsing the HTML content 
of web pages to collect structured information like text, images, links, or other elements.

## Difference:
- **Crawling**: Discovers URLs and navigates between pages
- **Scraping**: Extracts specific content from pages

## How to Use This Tool:

1. Run `hungry.bat` to start the program
2. Choose between crawling, scraping, or scraping all URLs mode
3. For crawling or single scraping:
   - Enter the target URL
   - Select your preferred output format (Markdown, JSON, or HTML)
4. For scraping all URLs:
   - Select a previously crawled URL file
   - Select your preferred output format
5. Use the Resume Crawl feature to continue a paused crawl
6. Use the Search feature to find content in your crawled/scraped data
7. Configure crawler behavior in Settings
8. Results will be saved in the "Results" folder
9. Crawled URLs will be saved in the "Crawled" folder
10. Exported data will be saved in the "Exports" folder

## Features:
- Robots.txt compliance
- Rate limiting to be respectful to servers
- Multiple export formats (JSON, CSV, TXT)
- Content search functionality
- Configurable settings
- Blacklist/whitelist URL filtering
- Proxy support
- User agent rotation
- Pause and resume crawls
- Export search results

## Tips:
- Use crawling to map websites and discover pages
- Use scraping to extract specific content from known pages
- Use "Scrape All URLs" to batch process previously crawled sites
- For large websites, use the pause/resume feature to split crawling into sessions
- Configure proxies in settings to avoid IP blocking on intensive crawls
- Respect website terms of service and robots.txt
- Avoid excessive requests that might overload servers
- Use the Settings menu to configure crawler behavior
    """
    
    # Content section with markdown
    layout["content"].update(Panel(
        Markdown(help_text),
        title=gradient_text("[ DOCUMENTATION ]", "bright_blue", "bright_magenta"),
        border_style="green",
        box=box.HEAVY
    ))
    
    # Display the layout
    console.print(layout)
    
    # Add a footer with keyboard shortcuts
    console.print("\n[bold cyan]Keyboard Shortcuts:[/bold cyan]")
    shortcuts_table = Table(box=box.SIMPLE)
    shortcuts_table.add_column("[bold]Key[/bold]", style="bright_yellow")
    shortcuts_table.add_column("[bold]Action[/bold]", style="bright_green")
    
    shortcuts_table.add_row("CTRL+C", "Exit program")
    shortcuts_table.add_row("Enter", "Confirm selection")
    shortcuts_table.add_row("1-8", "Quick menu navigation")
    
    console.print(shortcuts_table)
    
    # Add a "Press any key to return" message
    console.print("\n[bold yellow]Press Enter to return to main menu...[/bold yellow]")

def validate_url(url):
    """Validate if the URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain(url):
    """Extract domain from URL"""
    parsed_uri = urlparse(url)
    return '{uri.netloc}'.format(uri=parsed_uri)

def create_folders():
    """Create necessary folders if they don't exist"""
    for folder in ["Results", "Crawled", "Exports", "Logs"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            console.print(f"[green]Created {folder} folder[/green]")

def sanitize_filename(url):
    """Create a safe filename from URL"""
    domain = get_domain(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{domain}_{timestamp}"

def clean_text(text):
    """Clean text by removing or replacing problematic Unicode characters"""
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Replace common Unicode symbols with ASCII equivalents
    replacements = {
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u00a9': '(c)',# Copyright symbol
        '\u00ae': '(R)',# Registered trademark
        '\u2122': 'TM', # Trademark symbol
        '\u00a0': ' ',  # Non-breaking space
        '\u00b0': ' degrees', # Degree symbol
        '\u20ac': 'EUR', # Euro symbol
        '\u00a3': 'GBP', # Pound symbol
        '\u00a5': 'JPY', # Yen symbol
        '\u00a2': 'cents', # Cent symbol
    }
    
    # Replace known symbols
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove emojis and other special Unicode characters
    # This regex matches emoji characters and other non-ASCII symbols
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    
    # Replace any remaining problematic characters with a space
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def clean_and_format_html(html_content, url):
    """Clean and format HTML content for better readability"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(["script", "style", "iframe", "noscript"]):
        element.extract()
    
    # Add a CSS for better styling
    head = soup.head or soup.new_tag("head")
    if not soup.head:
        soup.html.insert(0, head)
    
    # Add meta charset if not present
    if not soup.find("meta", charset=True):
        meta_charset = soup.new_tag("meta")
        meta_charset["charset"] = "UTF-8"
        head.append(meta_charset)
    
    # Add viewport meta if not present
    if not soup.find("meta", attrs={"name": "viewport"}):
        meta_viewport = soup.new_tag("meta")
        meta_viewport["name"] = "viewport"
        meta_viewport["content"] = "width=device-width, initial-scale=1.0"
        head.append(meta_viewport)
    
    # Add title if not present
    if not soup.title:
        title_tag = soup.new_tag("title")
        title_tag.string = "Scraped Content"
        head.append(title_tag)
    
    # Add CSS styling
    style = soup.new_tag("style")
    style.string = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    h1 { font-size: 2.2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
    h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
    h3 { font-size: 1.5em; }
    h4 { font-size: 1.3em; }
    h5 { font-size: 1.2em; }
    h6 { font-size: 1.1em; }
    p { margin: 1em 0; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    img { max-width: 100%; height: auto; }
    pre, code {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 0.5em;
        overflow: auto;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .scraper-info {
        margin-top: 2em;
        padding-top: 1em;
        border-top: 1px solid #eee;
        font-size: 0.9em;
        color: #777;
    }
    """
    head.append(style)
    
    # Add a footer with scraping info
    footer = soup.new_tag("div")
    footer["class"] = "scraper-info"
    footer.string = f"Scraped from {url} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Hungry Crawler"
    
    # Find body or create it
    body = soup.body or soup.new_tag("body")
    if not soup.body:
        if soup.html:
            soup.html.append(body)
        else:
            html_tag = soup.new_tag("html")
            html_tag.append(body)
            soup.append(html_tag)
    
    body.append(footer)
    
    # Make all links absolute
    for a_tag in soup.find_all('a', href=True):
        if not a_tag['href'].startswith(('http://', 'https://', 'mailto:', 'tel:')):
            a_tag['href'] = urljoin(url, a_tag['href'])
    
    # Make all image sources absolute
    for img_tag in soup.find_all('img', src=True):
        if not img_tag['src'].startswith(('http://', 'https://', 'data:')):
            img_tag['src'] = urljoin(url, img_tag['src'])
    
    return soup.prettify()

def html_to_csv(html_content, url):
    """Convert HTML content to CSV format"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Clean up the HTML
    for script in soup(["script", "style"]):
        script.extract()
    
    # Extract title
    title = clean_text(soup.title.string if soup.title else "No Title")
    
    # First, try to find tables - they're the most natural fit for CSV
    tables = soup.find_all('table')
    if tables:
        # Use the first table found
        table = tables[0]
        rows = table.find_all('tr')
        
        csv_data = []
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
        
        if not headers and rows:
            # Try to get headers from first row
            headers = [clean_text(th.get_text()) for th in rows[0].find_all(['th', 'td'])]
            rows = rows[1:]  # Skip the header row
        
        # If still no headers, create generic ones
        if not headers and rows:
            first_row = rows[0].find_all(['td', 'th'])
            headers = [f"Column {i+1}" for i in range(len(first_row))]
        
        # Add headers to CSV
        csv_data.append(headers)
        
        # Add rows
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [clean_text(cell.get_text()) for cell in cells]
                csv_data.append(row_data)
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        return output.getvalue()
    
    # If no tables, create a structured CSV from page content
    else:
        # Extract headings
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading_text = clean_text(heading.get_text())
                if heading_text:
                    headings.append((i, heading_text))
        
        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            p_text = clean_text(p.get_text())
            if p_text:
                paragraphs.append(p_text)
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            link_text = clean_text(a.get_text()) or "Link"
            link_url = a['href']
            if not link_url.startswith(('http://', 'https://')):
                link_url = urljoin(url, link_url)
            links.append((link_text, link_url))
        
        # Create CSV data
        csv_data = []
        
        # Add metadata
        csv_data.append(["URL", url])
        csv_data.append(["Title", title])
        csv_data.append(["Scraped Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        csv_data.append([])  # Empty row as separator
        
        # Add headings section
        if headings:
            csv_data.append(["Headings", ""])
            for level, text in headings:
                csv_data.append([f"H{level}", text])
            csv_data.append([])  # Empty row as separator
        
        # Add paragraphs section
        if paragraphs:
            csv_data.append(["Paragraphs", ""])
            for i, text in enumerate(paragraphs, 1):
                csv_data.append([f"P{i}", text])
            csv_data.append([])  # Empty row as separator
        
        # Add links section
        if links:
            csv_data.append(["Links", ""])
            csv_data.append(["Text", "URL"])
            for text, url in links:
                csv_data.append([text, url])
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        return output.getvalue()

def save_to_file(data, url, file_type):
    """Save data to file in the specified format"""
    create_folders()
    base_filename = sanitize_filename(url)
    
    if file_type == "markdown" or file_type == "md":
        filename = os.path.join("Results", f"{base_filename}.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
    elif file_type == "json":
        filename = os.path.join("Results", f"{base_filename}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
    elif file_type == "csv":
        filename = os.path.join("Results", f"{base_filename}.csv")
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            f.write(data)
    else:  # HTML
        filename = os.path.join("Results", f"{base_filename}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
    
    return filename

def html_to_markdown(html_content):
    """Convert HTML content to Markdown with preserved formatting"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Clean up the HTML
    for script in soup(["script", "style"]):
        script.extract()
    
    # Clean and add headers
    title = clean_text(soup.title.string) if soup.title else 'Extracted Content'
    md_content = f"# {title}\n\n"
    
    # Extract metadata if available
    meta_section = ""
    meta_count = 0
    for meta in soup.find_all('meta'):
        if meta.get('name') and meta.get('content'):
            meta_name = clean_text(meta['name'])
            meta_content = clean_text(meta['content'])
            if meta_name and meta_content:
                meta_section += f"- **{meta_name}**: {meta_content}\n"
                meta_count += 1
    
    if meta_count > 0:
        md_content += "## Metadata\n\n" + meta_section + "\n\n"
    
    # Process main content - use a recursive approach for better nested element handling
    def process_element(element, level=0):
        if element.name is None:
            text = clean_text(element.string)
            return text if text else ""
        
        result = ""
        
        # Handle different element types
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading_level = int(element.name[1]) + 1  # Add 1 because we already have a level 1 heading
            heading_text = clean_text(element.get_text())
            if heading_text:
                result += f"\n{'#' * heading_level} {heading_text}\n\n"
        
        elif element.name == 'p':
            p_text = clean_text(element.get_text())
            if p_text:
                result += f"{p_text}\n\n"
        
        elif element.name == 'a' and element.has_attr('href'):
            link_text = clean_text(element.get_text()) or "Link"
            link_url = element['href']
            # Only process as standalone link if not inside another element we're handling
            if element.parent.name not in ['li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'th', 'td', 'p']:
                result += f"[{link_text}]({link_url})\n\n"
        
        elif element.name == 'img' and element.has_attr('src'):
            alt_text = clean_text(element.get('alt', 'Image'))
            img_src = element['src']
            result += f"![{alt_text}]({img_src})\n\n"
        
        elif element.name == 'ul':
            result += "\n"
            for li in element.find_all('li', recursive=False):
                li_text = clean_text(li.get_text())
                if li_text:
                    result += f"* {li_text}\n"
            result += "\n"
        
        elif element.name == 'ol':
            result += "\n"
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                li_text = clean_text(li.get_text())
                if li_text:
                    result += f"{i}. {li_text}\n"
            result += "\n"
        
        elif element.name == 'blockquote':
            blockquote_text = clean_text(element.get_text())
            if blockquote_text:
                # Split into lines and add > to each line
                blockquote_lines = blockquote_text.split('\n')
                for line in blockquote_lines:
                    if line.strip():
                        result += f"> {line}\n"
                result += "\n"
        
        elif element.name == 'pre':
            code = element.find('code')
            if code:
                code_text = code.get_text()
            else:
                code_text = element.get_text()
            
            if code_text:
                result += "```\n"
                result += code_text + "\n"
                result += "```\n\n"
        
        elif element.name == 'table':
            # Extract headers
            headers = []
            header_row = element.find('thead')
            if header_row:
                headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            if not headers and element.find('tr'):
                # Try to get headers from first row if thead not found
                headers = [clean_text(th.get_text()) for th in element.find('tr').find_all(['th', 'td'])]
            
            if headers:
                # Create markdown table header
                result += "| " + " | ".join(headers) + " |\n"
                result += "| " + " | ".join(['---'] * len(headers)) + " |\n"
                
                # Add table rows
                rows = element.find_all('tr')
                start_idx = 1 if not header_row else 0  # Skip first row if we used it for headers
                
                for row in rows[start_idx:]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_content = [clean_text(cell.get_text()) for cell in cells]
                        # Ensure we have enough cells to match headers
                        while len(row_content) < len(headers):
                            row_content.append("")
                        # Truncate if too many cells
                        row_content = row_content[:len(headers)]
                        result += "| " + " | ".join(row_content) + " |\n"
                
                result += "\n"
        
        # Process child elements that aren't handled by specific cases above
        elif element.name not in ['script', 'style', 'head', 'meta']:
            for child in element.children:
                result += process_element(child, level + 1)
        
        return result
    
    # Process the body content
    body = soup.body or soup
    for element in body.children:
        if element.name not in ['script', 'style', 'head']:
            md_content += process_element(element)
    
    # Add a dedicated links section for any links we might have missed
    links_section = "\n## Links\n\n"
    link_count = 0
    for a in soup.find_all('a', href=True):
        if a.parent.name not in ['li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'th', 'td']:
            link_text = clean_text(a.get_text()) or "Link"
            link_url = a['href']
            # Convert relative URLs to absolute if possible
            if not link_url.startswith(('http://', 'https://')):
                # We don't have the base URL here, so we'll just note it's relative
                link_url = f"{link_url} (relative link)"
            links_section += f"* [{link_text}]({link_url})\n"
            link_count += 1
    
    if link_count > 0:
        md_content += links_section + "\n"
    
    # Add a dedicated images section
    images_section = "\n## Images\n\n"
    image_count = 0
    for img in soup.find_all('img', src=True):
        alt_text = clean_text(img.get('alt', 'Image'))
        img_src = img['src']
        # Convert relative URLs to absolute if possible
        if not img_src.startswith(('http://', 'https://')):
            # We don't have the base URL here, so we'll just note it's relative
            img_src = f"{img_src} (relative link)"
        images_section += f"![{alt_text}]({img_src})\n"
        image_count += 1
    
    if image_count > 0:
        md_content += images_section
    
    # Remove excessive newlines
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    
    return md_content

def html_to_json(html_content, url):
    """Convert HTML content to JSON with more structured data"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title and clean it
    title = clean_text(soup.title.string if soup.title else "No Title")
    
    # Clean up the HTML
    for script in soup(["script", "style"]):
        script.extract()
    
    # Extract metadata
    metadata = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "title": title
    }
    
    # Add meta tags to metadata
    for meta in soup.find_all('meta'):
        if meta.get('name') and meta.get('content'):
            meta_name = clean_text(meta['name'])
            meta_content = clean_text(meta['content'])
            if meta_name and meta_content:
                metadata[meta_name] = meta_content
    
    # Extract headings with hierarchy
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            heading_text = clean_text(heading.get_text())
            if heading_text:
                headings.append({
                    "level": i,
                    "text": heading_text
                })
    
    # Extract paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        p_text = clean_text(p.get_text())
        if p_text:
            paragraphs.append(p_text)
    
    # Extract lists
    lists = []
    for ul in soup.find_all('ul'):
        items = []
        for li in ul.find_all('li'):
            li_text = clean_text(li.get_text())
            if li_text:
                items.append(li_text)
        if items:
            lists.append({
                "type": "unordered",
                "items": items
            })
    
    for ol in soup.find_all('ol'):
        items = []
        for li in ol.find_all('li'):
            li_text = clean_text(li.get_text())
            if li_text:
                items.append(li_text)
        if items:
            lists.append({
                "type": "ordered",
                "items": items
            })
    
    # Extract tables
    tables = []
    for table in soup.find_all('table'):
        table_data = {"headers": [], "rows": []}
        
        # Extract headers
        header_row = table.find('thead')
        if header_row:
            headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            table_data["headers"] = headers
        
        if not table_data["headers"] and table.find('tr'):
            # Try to get headers from first row if thead not found
            headers = [clean_text(th.get_text()) for th in table.find('tr').find_all(['th', 'td'])]
            table_data["headers"] = headers
        
        # Extract rows
        rows = table.find_all('tr')
        start_idx = 1 if table_data["headers"] and not header_row else 0
        
        for row in rows[start_idx:]:
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [clean_text(cell.get_text()) for cell in cells]
                table_data["rows"].append(row_data)
        
        if table_data["headers"] or table_data["rows"]:
            tables.append(table_data)
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        link_text = clean_text(a.get_text()) or "Link"
        link_url = a['href']
        # Convert relative URLs to absolute
        if not link_url.startswith(('http://', 'https://')):
            link_url = urljoin(url, link_url)
        links.append({
            "text": link_text,
            "url": link_url
        })
    
    # Extract images
    images = []
    for img in soup.find_all('img', src=True):
        img_src = img['src']
        # Convert relative URLs to absolute
        if not img_src.startswith(('http://', 'https://')):
            img_src = urljoin(url, img_src)
        img_alt = clean_text(img.get('alt', 'Image'))
        images.append({
            "src": img_src,
            "alt": img_alt,
            "width": img.get('width', ''),
            "height": img.get('height', '')
        })
    
    # Extract full text content
    text_content = clean_text(soup.get_text().strip())
    
    # Create JSON structure
    data = {
        "metadata": metadata,
        "content": {
            "headings": headings,
            "paragraphs": paragraphs,
            "lists": lists,
            "tables": tables,
            "links": links,
            "images": images,
            "full_text": text_content
        }
    }
    
    return json.dumps(data, indent=2)

def save_crawled_urls(urls, domain):
    """Save crawled URLs to a text file in the Crawled folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("Crawled", f"{domain}_{timestamp}.txt")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Crawled URLs for {domain}\n")
        f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total URLs: {len(urls)}\n\n")
        for url in urls:
            f.write(f"{url}\n")
    
    return filename

def export_data(data, format_type, filename_base):
    """Export data to various formats"""
    create_folders()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "csv" and isinstance(data, list):
        filename = os.path.join("Exports", f"{filename_base}_{timestamp}.csv")
        try:
            if data and isinstance(data[0], dict):
                keys = data[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)
            else:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for item in data:
                        writer.writerow([item])
            return filename
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    elif format_type == "txt" and isinstance(data, list):
        filename = os.path.join("Exports", f"{filename_base}_{timestamp}.txt")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{item}\n")
            return filename
        except Exception as e:
            logger.error(f"Error exporting to TXT: {e}")
            return None
    
    elif format_type == "json":
        filename = os.path.join("Exports", f"{filename_base}_{timestamp}.json")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return filename
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None
    
    return None

def is_url_allowed(url):
    """Check if URL is allowed based on blacklist/whitelist"""
    # If whitelist is provided, only allow URLs in the whitelist
    if SETTINGS["whitelist"]:
        for pattern in SETTINGS["whitelist"]:
            if pattern in url:
                return True
        return False
    
    # If blacklist is provided, block URLs in the blacklist
    if SETTINGS["blacklist"]:
        for pattern in SETTINGS["blacklist"]:
            if pattern in url:
                return False
    
    # Default to allowed
    return True

def save_crawl_state(domain, visited_urls, urls_to_visit, found_urls, page_count):
    """Save the current state of the crawl to allow resuming later"""
    if not SETTINGS["save_crawl_state"]:
        return
    
    create_folders()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    state_file = os.path.join("Crawled", f"{domain}_state_{timestamp}.json")
    
    state = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "page_count": page_count,
        "visited_urls": list(visited_urls),
        "urls_to_visit": urls_to_visit,
        "found_urls": found_urls
    }
    
    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Crawl state saved to {state_file}")
        return state_file
    except Exception as e:
        logger.error(f"Error saving crawl state: {e}")
        return None

def load_crawl_state():
    """Load a previously saved crawl state"""
    create_folders()
    
    state_files = [f for f in os.listdir("Crawled") if f.endswith("_state_.json")]
    
    if not state_files:
        console.print("[yellow]No saved crawl states found.[/yellow]")
        return None
    
    console.print("[bold cyan]Available saved crawl states:[/bold cyan]")
    
    state_table = Table(box=box.SIMPLE)
    state_table.add_column("[bold]#[/bold]", style="cyan", justify="center")
    state_table.add_column("[bold]Domain[/bold]", style="green")
    state_table.add_column("[bold]Date[/bold]", style="yellow")
    state_table.add_column("[bold]Pages[/bold]", style="magenta")
    
    states = []
    for i, filename in enumerate(state_files, 1):
        try:
            with open(os.path.join("Crawled", filename), 'r', encoding='utf-8') as f:
                state = json.load(f)
                states.append((filename, state))
                
                # Format date
                date = datetime.fromisoformat(state["timestamp"])
                formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                
                state_table.add_row(
                    str(i), 
                    state["domain"], 
                    formatted_date, 
                    str(state["page_count"])
                )
        except Exception as e:
            logger.error(f"Error loading state file {filename}: {e}")
    
    if not states:
        console.print("[yellow]No valid saved crawl states found.[/yellow]")
        return None
    
    console.print(state_table)
    
    choice = Prompt.ask(
        "\n[bold cyan]Select a state to resume by number[/bold cyan] (or 'cancel' to start new crawl)",
        choices=[str(i) for i in range(1, len(states) + 1)] + ["cancel"],
        default="cancel"
    )
    
    if choice.lower() == "cancel":
        return None
    
    filename, state = states[int(choice) - 1]
    console.print(f"[green]Resuming crawl of {state['domain']} with {state['page_count']} pages already crawled[/green]")
    return state

def crawl_website(start_url, resume_state=None):
    """Crawl a website starting from the given URL"""
    console.print(Panel("[bold blue]Starting Crawler...[/bold blue]", border_style="blue"))
    
    if resume_state:
        # Resume from saved state
        domain = resume_state["domain"]
        visited_urls = set(resume_state["visited_urls"])
        urls_to_visit = resume_state["urls_to_visit"]
        found_urls = resume_state["found_urls"]
        page_count = resume_state["page_count"]
    else:
        # Start new crawl
        if not validate_url(start_url):
            console.print("[bold red]Invalid URL. Please include http:// or https://[/bold red]")
            return
        
        domain = get_domain(start_url)
        visited_urls = set()
        urls_to_visit = [start_url]
        found_urls = []
        page_count = 0
    
    # Always use JSON format for crawling
    output_format = "json"
    continue_crawling = True
    
    # Create a session with retry logic and random user agent
    session = get_session()
    
    # Check robots.txt first
    if not check_robots_txt(start_url, session):
        if not Confirm.ask("[yellow]This site's robots.txt disallows crawling. Continue anyway?[/yellow]"):
            console.print("[red]Crawling cancelled due to robots.txt restrictions[/red]")
            return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        crawl_task = progress.add_task("[green]Crawling...", total=None)
        
        while urls_to_visit and continue_crawling:
            # Get the next URL to visit
            current_url = urls_to_visit.pop(0)
            
            # Skip if we've already visited this URL
            if current_url in visited_urls:
                continue
            
            # Update progress
            progress.update(crawl_task, description=f"[green]Crawling: {current_url[:50]}...")
            
            try:
                # Check if URL is allowed based on blacklist/whitelist
                if not is_url_allowed(current_url):
                    logger.info(f"Skipping blacklisted URL: {current_url}")
                    continue
                
                # Check robots.txt for this specific URL
                if not check_robots_txt(current_url, session):
                    logger.info(f"Skipping URL disallowed by robots.txt: {current_url}")
                    continue
                
                # Send a GET request to the URL
                response = session.get(current_url, timeout=SETTINGS["timeout"])
                
                # Skip if not HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    continue
                
                # Mark as visited
                visited_urls.add(current_url)
                found_urls.append(current_url)
                page_count += 1
                
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links on the page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)
                    
                    # Only follow links to the same domain
                    if get_domain(absolute_url) == domain and absolute_url not in visited_urls:
                        urls_to_visit.append(absolute_url)
                
                # Check if we've reached the page limit
                if page_count >= SETTINGS["max_pages"]:
                    progress.stop()
                    console.print(f"\n[yellow]Reached maximum page limit ({SETTINGS['max_pages']})[/yellow]")
                    
                    # Offer options: continue, pause, or stop
                    choice = Prompt.ask(
                        "[bold cyan]What would you like to do?[/bold cyan]",
                        choices=["continue", "pause", "stop"],
                        default="continue"
                    )
                    
                    if choice == "continue":
                        # Reset the counter and increase the limit
                        SETTINGS["max_pages"] += 100
                        progress.start()
                    elif choice == "pause":
                        # Save the current state and exit
                        state_file = save_crawl_state(domain, visited_urls, urls_to_visit, found_urls, page_count)
                        if state_file:
                            console.print(f"[green]Crawl state saved to: {state_file}[/green]")
                            console.print("[yellow]You can resume this crawl later from the main menu.[/yellow]")
                        return
                    else:
                        break
                elif page_count % 20 == 0:
                    progress.stop()
                    
                    # Offer options: continue, pause, or stop
                    choice = Prompt.ask(
                        f"\n[yellow]Crawled {page_count} pages.[/yellow] [bold cyan]What would you like to do?[/bold cyan]",
                        choices=["continue", "pause", "stop"],
                        default="continue"
                    )
                    
                    if choice == "continue":
                        progress.start()
                    elif choice == "pause":
                        # Save the current state and exit
                        state_file = save_crawl_state(domain, visited_urls, urls_to_visit, found_urls, page_count)
                        if state_file:
                            console.print(f"[green]Crawl state saved to: {state_file}[/green]")
                            console.print("[yellow]You can resume this crawl later from the main menu.[/yellow]")
                        return
                    else:
                        break
                
                # Respect crawl delay to be nice to the server
                time.sleep(SETTINGS["crawl_delay"])
                
            except requests.RequestException as e:
                console.print(f"[red]Error crawling {current_url}: {str(e)}[/red]")
                # Add a small delay before continuing to the next URL
                time.sleep(2)
            except Exception as e:
                console.print(f"[red]Unexpected error: {str(e)}[/red]")
                time.sleep(1)
    
    # Display results
    console.print(f"\n[bold green]Crawling completed![/bold green]")
    console.print(f"[green]Found {len(found_urls)} URLs on {domain}[/green]")
    
    # Skip saving to Results folder for crawling
    # Just save URLs to Crawled folder
    crawled_file = save_crawled_urls(found_urls, domain)
    
    # Export data in different formats
    export_files = []
    for format_type in SETTINGS["export_formats"]:
        if format_type in ["csv", "txt", "json"]:
            export_file = export_data(found_urls, format_type, f"crawl_{domain}")
            if export_file:
                export_files.append((format_type, export_file))
    
    console.print(f"[bold green]Crawled URLs saved to:[/bold green] [cyan]{crawled_file}[/cyan]")
    
    if export_files:
        console.print("[bold green]Exported data:[/bold green]")
        for format_type, file_path in export_files:
            console.print(f"  [cyan]{format_type.upper()}:[/cyan] {file_path}")

def check_robots_txt(url, session):
    """Check robots.txt for crawling permissions"""
    if not SETTINGS["respect_robots_txt"]:
        return True
    
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    try:
        response = session.get(robots_url, timeout=10)
        if response.status_code == 200:
            # Very basic robots.txt parsing
            content = response.text.lower()
            user_agent = SETTINGS["user_agent"].lower()
            
            # Check if our user agent or all agents are disallowed
            disallow_all = False
            disallow_paths = []
            
            lines = content.split('\n')
            current_agent = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('user-agent:'):
                    agent = line[11:].strip()
                    if agent == '*' or user_agent in agent:
                        current_agent = agent
                    else:
                        current_agent = None
                
                elif current_agent and line.startswith('disallow:'):
                    path = line[9:].strip()
                    if path == '/':
                        disallow_all = True
                    elif path:
                        disallow_paths.append(path)
            
            if disallow_all:
                logger.warning(f"robots.txt disallows crawling {parsed_url.netloc}")
                return False
            
            # Check if the URL path is in disallowed paths
            for path in disallow_paths:
                if parsed_url.path.startswith(path):
                    logger.warning(f"robots.txt disallows crawling {url}")
                    return False
                    
            return True
        else:
            # If robots.txt doesn't exist or can't be accessed, assume it's allowed
            return True
    except Exception as e:
        logger.error(f"Error checking robots.txt: {e}")
        return True  # Assume allowed if there's an error

def get_session():
    """Create a requests session with retry logic and random user agent"""
    # List of common user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        SETTINGS["user_agent"]
    ]
    
    # Create a session
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=SETTINGS["max_retries"],
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Set a random user agent if rotation is enabled
    if SETTINGS["rotate_user_agents"]:
        user_agent = random.choice(user_agents)
    else:
        user_agent = SETTINGS["user_agent"]
    
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    })
    
    # Configure proxies if enabled
    if SETTINGS["use_proxies"] and SETTINGS["proxies"]:
        proxy = random.choice(SETTINGS["proxies"])
        if proxy:
            session.proxies = {
                "http": proxy,
                "https": proxy
            }
            logger.info(f"Using proxy: {proxy}")
    
    return session

def scrape_website(url, output_format):
    """Scrape content from a specific URL"""
    console.print(Panel("[bold magenta]Starting Scraper...[/bold magenta]", border_style="magenta"))
    
    if not validate_url(url):
        console.print("[bold red]Invalid URL. Please include http:// or https://[/bold red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}[/bold magenta]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task1 = progress.add_task("[magenta]Fetching page...", total=100)
        
        try:
            # Create a session with retry logic and random user agent
            session = get_session()
            
            # Fetch the page
            progress.update(task1, advance=30, description="[magenta]Sending request...")
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            progress.update(task1, advance=30, description="[magenta]Parsing content...")
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            progress.update(task1, advance=20, description="[magenta]Processing data...")
            
            # Process based on selected format
            if output_format == "markdown" or output_format == "md":
                output_content = html_to_markdown(html_content)
                file_type = "markdown"
            elif output_format == "json":
                output_content = html_to_json(html_content, url)
                file_type = "json"
            elif output_format == "csv":
                output_content = html_to_csv(html_content, url)
                file_type = "csv"
            else:  # HTML - clean it up and format it nicely
                output_content = clean_and_format_html(html_content, url)
                file_type = "html"
            
            progress.update(task1, advance=20, description="[magenta]Saving results...")
            filename = save_to_file(output_content, url, file_type)
            
            # Complete the progress bar
            progress.update(task1, completed=100)
            
        except requests.RequestException as e:
            progress.stop()
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            
            # Provide more helpful error messages based on status code
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 403:
                    console.print("[yellow]The website is blocking access. This could be due to:[/yellow]")
                    console.print("  - The site has anti-scraping protection")
                    console.print("  - Your IP might be temporarily blocked")
                    console.print("  - The site requires authentication")
                    console.print("\n[green]Suggestions:[/green]")
                    console.print("  - Try a different website")
                    console.print("  - Wait a while before trying again")
                    console.print("  - Check if the site has an official API")
                elif status_code == 404:
                    console.print("[yellow]The page was not found. Please check if the URL is correct.[/yellow]")
                elif status_code == 429:
                    console.print("[yellow]Too many requests. The website is rate-limiting your access.[/yellow]")
                    console.print("[green]Try again after waiting for a while.[/green]")
                elif status_code >= 500:
                    console.print("[yellow]The server encountered an error. This is not your fault.[/yellow]")
                    console.print("[green]Try again later when the server might be more stable.[/green]")
            return
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
            return
    
    # Display results
    console.print(f"\n[bold green]Scraping completed![/bold green]")
    
    # Show a summary of what was extracted
    table = Table(title="Scraping Summary", box=box.ROUNDED)
    table.add_column("Element", style="cyan")
    table.add_column("Count", style="magenta")
    
    # Count elements
    images_count = len(soup.find_all('img', src=True))
    paragraphs_count = len(soup.find_all('p'))
    headings_count = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    
    table.add_row("Images", str(images_count))
    table.add_row("Paragraphs", str(paragraphs_count))
    table.add_row("Headings", str(headings_count))
    
    console.print(table)
    console.print(f"[bold green]Results saved to:[/bold green] [cyan]{filename}[/cyan]")

def list_crawled_files():
    """List all crawled URL files and let user select one"""
    create_folders()
    
    crawled_files = [f for f in os.listdir("Crawled") if f.endswith(".txt")]
    
    if not crawled_files:
        console.print("[yellow]No crawled URL files found. Please crawl a website first.[/yellow]")
        return None
    
    console.print("[bold cyan]Available crawled URL files:[/bold cyan]")
    
    file_table = Table(box=box.SIMPLE)
    file_table.add_column("[bold]#[/bold]", style="cyan", justify="center")
    file_table.add_column("[bold]Filename[/bold]", style="green")
    file_table.add_column("[bold]Date[/bold]", style="yellow")
    
    for i, filename in enumerate(crawled_files, 1):
        # Try to extract date from filename
        date_match = re.search(r'_(\d{8}_\d{6})\.txt$', filename)
        if date_match:
            date_str = date_match.group(1)
            try:
                date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted_date = "Unknown"
        else:
            formatted_date = "Unknown"
            
        file_table.add_row(str(i), filename, formatted_date)
    
    console.print(file_table)
    
    choice = Prompt.ask(
        "\n[bold cyan]Select a file by number[/bold cyan]",
        choices=[str(i) for i in range(1, len(crawled_files) + 1)],
        default="1"
    )
    
    selected_file = crawled_files[int(choice) - 1]
    return os.path.join("Crawled", selected_file)

def scrape_all_urls(output_format):
    """Scrape all URLs from a crawled file"""
    crawled_file = list_crawled_files()
    
    if not crawled_file:
        return
    
    console.print(f"[bold green]Selected:[/bold green] [cyan]{crawled_file}[/cyan]")
    
    # Read URLs from the file
    urls = []
    with open(crawled_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    
    if not urls:
        console.print("[yellow]No URLs found in the file.[/yellow]")
        return
    
    console.print(f"[green]Found {len(urls)} URLs to scrape.[/green]")
    
    # Ask for confirmation
    if not Confirm.ask(f"[yellow]Do you want to scrape all {len(urls)} URLs?[/yellow]"):
        return
    
    # Scrape each URL
    successful = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}[/bold magenta]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[magenta]Scraping URLs...", total=len(urls))
        
        for i, url in enumerate(urls, 1):
            progress.update(task, description=f"[magenta]Scraping URL {i}/{len(urls)}...")
            
            try:
                # Create a session with retry logic and random user agent
                session = get_session()
                
                # Fetch the page
                response = session.get(url, timeout=15)
                response.raise_for_status()
                
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Process based on selected format
                if output_format == "markdown" or output_format == "md":
                    output_content = html_to_markdown(html_content)
                    file_type = "markdown"
                elif output_format == "json":
                    output_content = html_to_json(html_content, url)
                    file_type = "json"
                elif output_format == "csv":
                    output_content = html_to_csv(html_content, url)
                    file_type = "csv"
                else:  # HTML - clean it up and format it nicely
                    output_content = clean_and_format_html(html_content, url)
                    file_type = "html"
                
                save_to_file(output_content, url, file_type)
                successful += 1
                
            except Exception as e:
                failed += 1
                # Just log the error and continue with the next URL
                progress.console.print(f"[red]Error scraping {url}: {str(e)}[/red]")
                time.sleep(1)
            
            # Update progress
            progress.update(task, advance=1)
            
            # Add a small delay between requests to be nice to the server
            time.sleep(random.uniform(1, 3))
    
    console.print(f"\n[bold green]Batch scraping completed![/bold green]")
    console.print(f"[green]Successfully scraped: {successful} URLs[/green]")
    if failed > 0:
        console.print(f"[yellow]Failed to scrape: {failed} URLs[/yellow]")
    console.print(f"[green]Results saved to the Results folder[/green]")

def export_search_results(results, search_term):
    """Export search results to a file"""
    if not results:
        return None
    
    create_folders()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("Exports", f"search_{search_term.replace(' ', '_')}_{timestamp}.json")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "search_term": search_term,
                "timestamp": datetime.now().isoformat(),
                "result_count": len(results),
                "results": results
            }, f, indent=2)
        return filename
    except Exception as e:
        logger.error(f"Error exporting search results: {e}")
        return None

def search_crawled_content():
    """Search through crawled content"""
    create_folders()
    
    # Get all result files
    result_files = []
    for ext in ['.json', '.md', '.html']:
        result_files.extend(list(Path("Results").glob(f"*{ext}")))
    
    if not result_files:
        console.print("[yellow]No result files found. Please crawl or scrape some content first.[/yellow]")
        return
    
    # Ask for search term
    search_term = Prompt.ask("[bold cyan]Enter search term[/bold cyan]").lower()
    
    if not search_term:
        console.print("[yellow]No search term provided.[/yellow]")
        return
    
    console.print(f"[bold green]Searching for:[/bold green] [cyan]{search_term}[/cyan]")
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        search_task = progress.add_task("[green]Searching...", total=len(result_files))
        
        for file_path in result_files:
            progress.update(search_task, description=f"[green]Searching: {file_path.name}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                if search_term in content:
                    # Extract a snippet of text around the search term
                    start = max(0, content.find(search_term) - 50)
                    end = min(len(content), content.find(search_term) + len(search_term) + 50)
                    snippet = content[start:end]
                    
                    # Clean up the snippet
                    snippet = snippet.replace('\n', ' ').strip()
                    if start > 0:
                        snippet = f"...{snippet}"
                    if end < len(content):
                        snippet = f"{snippet}..."
                    
                    results.append({
                        "file": str(file_path),
                        "snippet": snippet
                    })
            except Exception as e:
                logger.error(f"Error searching file {file_path}: {e}")
            
            progress.update(search_task, advance=1)
    
    # Display results
    if results:
        console.print(f"\n[bold green]Found {len(results)} matches:[/bold green]")
        
        result_table = Table(box=box.ROUNDED)
        result_table.add_column("File", style="cyan")
        result_table.add_column("Snippet", style="yellow")
        
        for result in results:
            file_name = os.path.basename(result["file"])
            result_table.add_row(file_name, result["snippet"])
        
        console.print(result_table)
        
        # Ask if user wants to export results
        if Confirm.ask("[bold cyan]Would you like to export these search results?[/bold cyan]"):
            export_file = export_search_results(results, search_term)
            if export_file:
                console.print(f"[green]Search results exported to: {export_file}[/green]")
    else:
        console.print("[yellow]No matches found.[/yellow]")

def edit_settings():
    """Edit crawler settings"""
    settings = load_settings()
    
    console.print("[bold cyan]Current Settings:[/bold cyan]")
    
    settings_table = Table(box=box.ROUNDED)
    settings_table.add_column("Setting", style="green")
    settings_table.add_column("Value", style="yellow")
    
    for key, value in settings.items():
        if isinstance(value, list):
            value_str = ", ".join(value) if value else "None"
        else:
            value_str = str(value)
        settings_table.add_row(key, value_str)
    
    console.print(settings_table)
    
    # Ask which setting to edit
    setting_to_edit = Prompt.ask(
        "\n[bold cyan]Which setting would you like to edit?[/bold cyan] (or 'cancel' to go back)",
        default="cancel"
    )
    
    if setting_to_edit.lower() == 'cancel':
        return
    
    if setting_to_edit not in settings:
        console.print("[red]Invalid setting name.[/red]")
        return
    
    # Get current value
    current_value = settings[setting_to_edit]
    
    # Ask for new value
    if isinstance(current_value, bool):
        new_value = Confirm.ask(f"[bold cyan]Enable {setting_to_edit}?[/bold cyan]", default=current_value)
    elif isinstance(current_value, int):
        new_value = int(Prompt.ask(f"[bold cyan]Enter new value for {setting_to_edit}[/bold cyan]", default=str(current_value)))
    elif isinstance(current_value, float):
        new_value = float(Prompt.ask(f"[bold cyan]Enter new value for {setting_to_edit}[/bold cyan]", default=str(current_value)))
    elif isinstance(current_value, list):
        current_str = ", ".join(current_value) if current_value else ""
        new_str = Prompt.ask(
            f"[bold cyan]Enter comma-separated values for {setting_to_edit}[/bold cyan]",
            default=current_str
        )
        new_value = [item.strip() for item in new_str.split(",")] if new_str else []
    else:
        new_value = Prompt.ask(f"[bold cyan]Enter new value for {setting_to_edit}[/bold cyan]", default=str(current_value))
    
    # Update setting
    settings[setting_to_edit] = new_value
    
    # Save settings
    with open("settings.json", 'w') as f:
        json.dump(settings, f, indent=4, sort_keys=True)
    
    console.print(f"[green]Updated {setting_to_edit} to: {new_value}[/green]")
    
    # Update global settings
    global SETTINGS
    SETTINGS = settings

def check_for_updates():
    """Check if a new version is available"""
    try:
        # This would normally check a remote server
        # For now, we'll just simulate it
        latest_version = VERSION
        
        if latest_version != VERSION:
            console.print(f"[yellow]A new version ({latest_version}) is available![/yellow]")
            console.print("[cyan]Visit https://github.com/yourusername/hungry-crawler for updates.[/cyan]")
        return latest_version
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return None

# Set up signal handler for graceful exit
def signal_handler(sig, frame):
    """Handle signals like CTRL+C"""
    safe_exit()

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def display_animated_progress(task_description, total=100, duration=1):
    """Display a simplified progress bar"""
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[green]{task_description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(task_description, total=total)
        
        # Simulate progress
        chunk_size = total / (duration * 10)  # Update 10 times per second
        while not progress.finished:
            progress.update(task, advance=chunk_size)
            time.sleep(0.1)

def display_main_menu():
    """Display the main menu with a cyberpunk aesthetic"""
    # Read ASCII art from file
    try:
        with open("ascii.md", "r", encoding="utf-8") as f:
            header_text = f.read()
            # Ensure we have content
            if not header_text.strip():
                raise FileNotFoundError("ASCII art file is empty")
    except Exception as e:
        # Log the error
        logger.error(f"Error reading ASCII art: {e}")
        # Fallback if file can't be read
        header_text = "MAIN MENU"
    
    # Apply gradient color effect to the ASCII art
    lines = header_text.split('\n')
    gradient_header = ""
    
    # Define gradient colors from blue to cyan to green
    gradient_colors = ["bright_blue", "blue", "cyan", "bright_cyan", "green", "bright_green"]
    
    # Apply gradient to each line
    for i, line in enumerate(lines):
        # Calculate color index based on position in the ASCII art
        color_idx = min(i % len(gradient_colors), len(gradient_colors) - 1)
        gradient_header += f"[{gradient_colors[color_idx]}]{line}[/{gradient_colors[color_idx]}]\n"
    
    # Create a panel with the gradient header
    header = Panel(
        gradient_header,
        border_style="cyan",
        box=box.HEAVY_EDGE
    )
    console.print(header)
    
    # Create a simple welcome message
    console.print(Panel(
        Align.center("[cyan]Welcome to the Hungry Crawler & Scraper![/cyan]"),
        subtitle=f"[green]v{VERSION}[/green]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    # Create a simple menu table with consistent colors
    mode_table = Table(box=box.SIMPLE_HEAVY)
    mode_table.add_column("[bold]#[/bold]", style="cyan", justify="center")
    mode_table.add_column("[bold]Mode[/bold]", style="green")
    mode_table.add_column("[bold]Description[/bold]", style="white")
    
    # Add rows with consistent styling
    mode_table.add_row("1", "[bold]Crawl[/bold]", "Discover and map all pages on a website")
    mode_table.add_row("2", "[bold]Scrape[/bold]", "Extract content from a specific page")
    mode_table.add_row("3", "[bold]Scrape All URLs[/bold]", "Scrape all URLs from a previous crawl")
    mode_table.add_row("4", "[bold]Resume Crawl[/bold]", "Resume a previously paused crawl")
    mode_table.add_row("5", "[bold]Search[/bold]", "Search through crawled content")
    mode_table.add_row("6", "[bold]Settings[/bold]", "Configure crawler settings")
    mode_table.add_row("7", "[bold]Help[/bold]", "Show help documentation")
    mode_table.add_row("8", "[bold]Exit[/bold]", "Quit the program")
    
    # Wrap the table in a panel with consistent colors
    menu_panel = Panel(
        mode_table,
        title="[cyan][ SELECT OPERATION ][/cyan]",
        border_style="cyan",
        box=box.HEAVY
    )
    console.print(menu_panel)
    
    # Add a simple footer with system status
    status_text = f"[dim]System Status: [green]ONLINE[/green] | Memory: [cyan]OPTIMAL[/cyan] | Network: [green]CONNECTED[/green][/dim]"
    console.print(Align.center(status_text))

def main():
    """Main function to run the crawler/scraper"""
    # Clear the console and display the banner
    console.clear()
    display_banner()
    
    # Check for updates
    check_for_updates()
    
    # Check for help argument
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['/help', '-h', '--help', 'help']:
        display_help()
        return
    
    while True:
        # Clear console and display main menu
        console.clear()
        display_main_menu()
        
        # Create a simple prompt with consistent colors
        console.print("\n[cyan]SELECT OPERATION[/cyan] [green](1-8)[/green]:")
        
        mode_choice = Prompt.ask(
            "",
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "crawl", "scrape", "scrape-all", "resume", "search", "settings", "help", "exit"],
            default="1"
        )
        
        # Show a loading animation when selecting an option
        display_animated_progress(f"Loading {mode_choice.upper()} module", duration=1)
        console.clear()
        
        if mode_choice in ["7", "help"]:
            display_help()
            input()  # Wait for Enter key
            continue
        elif mode_choice in ["8", "exit"]:
            safe_exit()
        elif mode_choice in ["5", "search"]:
            # Display a simple search banner
            search_banner = pyfiglet.figlet_format("SEARCH", font="small")
            console.print(f"[cyan]{search_banner}[/cyan]")
            
            search_crawled_content()
            # Ask user to press Enter to continue
            console.print("\n[green]Press Enter to return to the main menu...[/green]")
            input()
            continue
        elif mode_choice in ["6", "settings"]:
            # Display a simple settings banner
            settings_banner = pyfiglet.figlet_format("SETTINGS", font="small")
            console.print(f"[cyan]{settings_banner}[/cyan]")
            
            edit_settings()
            # Ask user to press Enter to continue
            console.print("\n[green]Press Enter to return to the main menu...[/green]")
            input()
            continue
        elif mode_choice in ["4", "resume"]:
            # Display a simple resume banner
            resume_banner = pyfiglet.figlet_format("RESUME CRAWL", font="small")
            console.print(f"[cyan]{resume_banner}[/cyan]")
            
            # Resume a previously saved crawl
            resume_state = load_crawl_state()
            if resume_state:
                crawl_website(None, resume_state)
                # Ask user to press Enter to continue
                console.print("\n[green]Press Enter to return to the main menu...[/green]")
                input()
            continue
        elif mode_choice in ["3", "scrape-all"]:
            # Ask for output format
            format_table = Table(box=box.SIMPLE)
            format_table.add_column("[bold]Option[/bold]", style="cyan", justify="center")
            format_table.add_column("[bold]Format[/bold]", style="green")
            format_table.add_column("[bold]Description[/bold]", style="yellow")
            
            format_table.add_row("1", "Markdown", "Clean, readable text format")
            format_table.add_row("2", "JSON", "Structured data format")
            format_table.add_row("3", "HTML", "Original web format")
            format_table.add_row("4", "CSV", "Spreadsheet-compatible format")
            
            console.print(format_table)
            
            format_choice = Prompt.ask(
                "\n[bold cyan]Would you like to convert to markdown, JSON, CSV or keep as HTML?[/bold cyan]",
                choices=["1", "2", "3", "4", "md", "markdown", "json", "html", "csv"],
                default="1"
            )
            
            # Map choices to formats
            format_map = {
                "1": "markdown",
                "2": "json",
                "3": "html",
                "4": "csv",
                "md": "markdown",
                "markdown": "markdown",
                "json": "json",
                "html": "html",
                "csv": "csv"
            }
            output_format = format_map[format_choice.lower()]
            
            # Scrape all URLs from a crawled file
            scrape_all_urls(output_format)
            
            # Ask user to press Enter to continue
            console.print("\n[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
            input()
            continue
        
        # Display appropriate banner based on mode with consistent colors
        if mode_choice in ["1", "crawl"]:
            mode_banner = pyfiglet.figlet_format("CRAWLER", font="small")
            console.print(f"[cyan]{mode_banner}[/cyan]")
        elif mode_choice in ["2", "scrape"]:
            mode_banner = pyfiglet.figlet_format("SCRAPER", font="small")
            console.print(f"[cyan]{mode_banner}[/cyan]")
        elif mode_choice in ["3", "scrape-all"]:
            mode_banner = pyfiglet.figlet_format("BATCH SCRAPER", font="small")
            console.print(f"[cyan]{mode_banner}[/cyan]")
        
        # Get URL with a simple prompt
        mode_text = "crawl" if mode_choice in ["1", "crawl"] else "scrape"
        
        url_panel = Panel(
            "[dim]Enter the full URL including http:// or https://[/dim]",
            title=f"[cyan]TARGET URL TO {mode_text.upper()}[/cyan]",
            border_style="cyan"
        )
        console.print(url_panel)
        
        url = Prompt.ask("\n[green]URL[/green]")
        
        # Validate URL with simple feedback
        if not validate_url(url):
            error_panel = Panel(
                "[red]The URL you entered is invalid![/red]\n\nPlease make sure to include http:// or https:// prefix.",
                title="[red]ERROR[/red]",
                border_style="red",
                box=box.HEAVY
            )
            console.print(error_panel)
            
            # Ask user to press Enter to continue
            console.print("\n[green]Press Enter to return to the main menu...[/green]")
            input()
            continue
        
        # For crawling, skip asking for output format
        if mode_choice in ["1", "crawl"]:
            # For crawling, we don't need to ask for output format as it defaults to JSON
            crawl_website(url)
        else:
            # For scraping, ask for the output format
            format_table = Table(box=box.SIMPLE)
            format_table.add_column("[bold]Option[/bold]", style="cyan", justify="center")
            format_table.add_column("[bold]Format[/bold]", style="green")
            format_table.add_column("[bold]Description[/bold]", style="yellow")
            
            format_table.add_row("1", "Markdown", "Clean, readable text format")
            format_table.add_row("2", "JSON", "Structured data format")
            format_table.add_row("3", "HTML", "Original web format")
            
            console.print(format_table)
            
            format_choice = Prompt.ask(
                "\n[bold cyan]Would you like to convert to markdown, JSON or keep as HTML?[/bold cyan]",
                choices=["1", "2", "3", "md", "markdown", "json", "html"],
                default="1"
            )
            
            # Map choices to formats
            format_map = {
                "1": "markdown",
                "2": "json",
                "3": "html",
                "md": "markdown",
                "markdown": "markdown",
                "json": "json",
                "html": "html"
            }
            output_format = format_map[format_choice.lower()]
            
            # Execute scraping with the selected format
            scrape_website(url, output_format)
        
        # Ask user to press Enter to continue
        console.print("\n[bold cyan]Press Enter to return to the main menu...[/bold cyan]")
        input()

def safe_exit():
    """Safely exit the program without triggering additional exceptions"""
    try:
        display_exit_animation()
    except:
        # If display_exit_animation fails, force exit
        os._exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        safe_exit()
    except Exception as e:
        try:
            console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
            console.print("[yellow]Press Enter to exit...[/yellow]")
            input()
            safe_exit()
        except:
            # If even the error handling fails, force exit
            os._exit(0)
