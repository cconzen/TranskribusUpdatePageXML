# Transkribus PageXML Batch Updater

This Python script automates the process of updating one or multiple documents in Transkribus by exchanging their PageXML files using Transkribus' REST API. 
It logs in to the Transkribus server, retrieves documents and their pages, and updates the corresponding XML metadata for each page from locally stored files.

## Requirements

- Python 3.x
- `requests` library

You can install `requests` using pip:

```
pip install requests
```

