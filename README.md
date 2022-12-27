# Mediafire Downloader
A simple command-line script to download files from mediafire.com using a list of URLs provided in a CSV file. The script handles confirmation prompts and displays a progress bar using the requests and tqdm libraries. Optional arguments allow specification of input CSV file and output folder for downloaded files.

## Usage

```python
python mediafire-dl.py [-o OUTPUT_FOLDER] [csv_file]
```

## Arguments
- `csv_file`: Path to CSV file with URLs (optional, default: `urls.csv`)
- `--output-folder`, `-o`: Output folder for downloaded files (optional, default: `download`)

## References
- This script is based on the [mediafire-dl](https://github.com/Juvenal-Yescas/mediafire-dl) script by **Juvenal Yescas**.
- The `requests` library is used for sending HTTP requests and downloading the files.
- The `tqdm` library is used for displaying the progress bar.
- The `argparse` library is used for parsing command-line arguments.
- The `csv` library is used for reading the input CSV file.
- The `os` and `os.path` libraries are used for working with file and directory paths.
- The `re` library is used for regular expression matching.
- The `shutil` library is used for moving files.
- The `tempfile` library is used for creating temporary files.

## Error
If an error occurs during the download process or if the URL is invalid, the script will output a text file containing the error message and the URL to the `error_log.txt` file, with each error message and URL on a separate line.