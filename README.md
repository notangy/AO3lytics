Special mention to [ao3-stats-exporter](https://github.com/Mircoxi/ao3-stats-exporter) for laying the groundwork for this project!

# AO3Lytics

A lightweight command line tool for those who use archiveofourown.org (aka AO3).
Able to export both work and stat data from your statistics page, as well as saving your bookmarks.

- Run the script on a schedule to gather consistent metrics from your own statistics, or just adhoc!
- Keep an offline record of your bookmarks: when a work you saved years ago ends up deleted, no more wondering what it was about 🤔

# CLI (command line interface)

There are two parts to the CLI tool:

- stat_parser: logs into your account and parses the HTML from your statistics page, saving both your user and work stats as JSON.
- bookmark_savior: visits your bookmarks page and parses the HTML, visiting each page up to a certain limit (this can be changed in the code) and saving the results as JSON.

Each resulting file is named in the folder `cli/stat_output` with a timestamp of when it was created, allowing you to gather snapshots of both pages over time.

To run the tool, make sure you have a .env file with the following information:

```
AO3_USERNAME =
AO3_PASSWORD =
```

The script needs these credentials in order to login. Then from within the directory run:

    python3 cli/ao3lytics.py

Pass in optional arguments `--skip_stats` or `--skip_bookmarks` if you want to skip over those steps.

(If you only want to gather bookmarks, `bookmark_savior` can also be run on its own since it doesn't require login.)

<!-- - See graphs of your own statistics: fandom breakdowns by year, word count growth, etc -->

<!-- # How is data gathered & stored?

When `stat_parser.py` runs, it logs in to AO3 with your credentials and makes a requests to your own statistics page. The HTML of this page is parsed for the details of all the works within it. This data is then saved to an external .json file with a timestamp in the file name.

This .json can be fed into a metrics platform (e.g. Prometheus) or into a local database for querying.

**Note:** The web application bundled with this repo expects that the data will be accessible over MongoDB, but you can reconfigure it to your own needs.

# Does this scrape data from AO3?

It is not a 'data scraper' in the sense that it mass-downloads hundreds of pages at a time. The only data pulled is your own work and user data, which remains completely inaccesible to anyone other than yourself and whoever you choose to share it with. It also saves data relating to your bookmarks and 'marked for later' queues. Every effort is made to reduce load on AO3's servers by only fetching new data once and then saving it locally for querying.

# How do I run it?

WIP -->
