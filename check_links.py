
import os
import re
import requests
import csv
from urllib.parse import urlparse, urljoin

# Configuration
start_dir = "."
output_csv = "brokenlinks.csv"
exclude_dirs = ["node_modules", ".git", "profile", "outputs", ".config"]
file_extensions = [".md", ".MDX", ".html", ".json", ".yaml", ".py", ".ipynb"]

# Regular expression to find URLs
url_regex = re.compile(r'https?://[^\s)"\'<>]+')
# Regular expression to find relative links in markdown and html
md_html_relative_link_regex = re.compile(r'\]\((?!https?:\/\/)([^)]+)\)|href="(?!https?:\/\/)([^"]+)"')
# Generic regex for other file types to find path-like strings
generic_relative_link_regex = re.compile(r'[\'"]((?:\.\/|\.\.\/)[^\'"\s]+|[^\'"\s]+\/[^\'"\s]*)[\'"]')


def is_valid_url(url):
    """Checks if a URL has a valid format."""
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

def check_external_link(url):
    """Checks a single URL and returns the status."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code
    except requests.RequestException as e:
        return str(e)

def check_internal_link(link, base_path):
    """Checks if an internal link is valid."""
    # Handle anchors by stripping them
    link_path = link.split('#')[0]
    if not link_path:
        return 200 # It's just an anchor

    # Handle root-relative paths
    if link_path.startswith('/'):
        abs_path = os.path.abspath(os.path.join(start_dir, link_path[1:]))
    else:
        abs_path = os.path.abspath(os.path.join(os.path.dirname(base_path), link_path))

    if os.path.exists(abs_path):
        return 200 # OK
    else:
        return "File not found"

def find_links_in_file(filepath):
    """Finds all links in a given file."""
    links = set()
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Find absolute URLs
            absolute_links = url_regex.findall(content)
            for link in absolute_links:
                links.add(link)
            # Find relative links
            relative_links = md_html_relative_link_regex.findall(content)
            # The regex returns tuples of groups, so we need to flatten the list
            for t in relative_links:
                for item in t:
                    if item:
                        links.add(item)

            # Find generic relative links for non-markup files
            generic_links = generic_relative_link_regex.findall(content)
            for link in generic_links:
                if link:
                    links.add(link)

    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
    return list(links)

def main():
    """Main function to scan files and check links."""
    broken_links = []

    for root, dirs, files in os.walk(start_dir, topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                filepath = os.path.join(root, file)
                links = find_links_in_file(filepath)

                for link in links:
                    if is_valid_url(link):
                        status = check_external_link(link)
                        if not isinstance(status, int) or status >= 400:
                            broken_links.append({
                                "File": filepath,
                                "URL": link,
                                "Status": status
                            })
                            print(f"Broken external link found in {filepath}: {link} ({status})")
                    else:
                        # This is an internal link
                        status = check_internal_link(link, filepath)
                        if status != 200:
                            broken_links.append({
                                "File": filepath,
                                "URL": link,
                                "Status": status
                            })
                            print(f"Broken internal link found in {filepath}: {link} ({status})")

    # Write broken links to CSV
    if broken_links:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["File", "URL", "Status"])
            writer.writeheader()
            writer.writerows(broken_links)
        print(f"\nFound {len(broken_links)} broken links. Report saved to {output_csv}")
    else:
        print("\nNo broken links found.")

if __name__ == "__main__":
    main()
