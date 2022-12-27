import argparse
import csv
import os
import os.path as osp
import re
import shutil
import sys
import tempfile

import requests
import tqdm

CHUNK_SIZE = 512 * 1024  # 512KB


def extractDownloadLink(contents):
    for line in contents.splitlines():
        m = re.search(r'href="((http|https)://download[^"]+)', line)
        if m:
            return m.groups()[0]


def download(url, output_folder, quiet):
    global pbar
    url_origin = url
    sess = requests.session()

    while True:
        res = sess.get(url, stream=True)
        if 'Content-Disposition' in res.headers:
            # This is the file
            break

        # Need to redirect with confirmation
        url = extractDownloadLink(res.text)

        if url is None:
            print('Permission denied: %s' % url_origin, file=sys.stderr)
            print(
                "Maybe you need to change permission over "
                "'Anyone with the link'?",
                file=sys.stderr,
            )
            return

    # Use the file's original name if it was provided in the
    # 'Content-Disposition' header, or the base name of the URL if no such
    # header was provided
    if 'Content-Disposition' in res.headers:
        m = re.search(
            'filename="(.*)"', res.headers['Content-Disposition']
        )
        output_name = m.groups()[0]
    else:
        output_name = osp.basename(url)

    # Join the output folder and the output file name to get the full output
    # path
    output_path = osp.join(output_folder, output_name)

    if not quiet:
        print('Downloading...', file=sys.stderr)
        print('From:', url_origin, file=sys.stderr)
        print('To:', output_path, file=sys.stderr)

    # Create a temporary file in the output folder
    tmp_file = tempfile.mktemp(
        suffix=tempfile.template,
        prefix=output_name,
        dir=output_folder,
    )
    f = open(tmp_file, 'wb')

    try:
        total = res.headers.get('Content-Length')
        if total is not None:
            total = int(total)
        if not quiet:
            pbar = tqdm.tqdm(total=total, unit='B', unit_scale=True)
        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
            if not quiet:
                pbar.update(len(chunk))
        if not quiet:
            pbar.close()
        f.close()
        shutil.move(tmp_file, output_path)
    except IOError as e:
        print(e, file=sys.stderr)
        return
    finally:
        try:
            if tmp_file:
                os.remove(tmp_file)
        except OSError:
            pass
        return output_path


def main():
    desc = 'Simple command-line script to download files from mediafire'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        'csv_file',
        help='Path to CSV file with URLs',
        nargs='?',  # Make the argument optional
        default='urls.csv',  # Use 'urls.csv' as the default CSV file
    )
    parser.add_argument(
        '--output-folder', '-o',
        help='Output folder for downloaded files',
        default='download',  # Use 'download' as the default output folder
    )
    args = parser.parse_args()

    # Read URLs from CSV file
    with open(args.csv_file, 'r') as f:
        reader = csv.reader(f)
        urls = [row[0] for row in reader]

    # Create output folder if it does not exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Open error log file (create if it does not exist)
    error_log_path = osp.join(args.output_folder, 'error_log.txt')
    error_log_file = open(error_log_path, 'w')

    # Download files
    for i, url in enumerate(urls):
        try:
            output_path = download(url, args.output_folder, quiet=False)
        except Exception as e:
            print(f'Error downloading file from URL {url}: {e}', file=sys.stderr)
            error_log_file.write(f'{i + 1}, {url}\n')
        else:
            if not output_path:
                error_log_file.write(f'{i + 1}, {url}\n')
    error_log_file.close()


if __name__ == '__main__':
    main()
