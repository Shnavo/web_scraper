import sys
from crawl import crawl_page


def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    url = sys.argv[1]
    print(f"starting crawl of: {url}\n")
    data = crawl_page(url)
    print(f"\nReturned {len(data)} sites\n")
    print("Headings of each page:")
    for page in data:
        print(data[page]["heading"])


if __name__ == "__main__":
    main()
