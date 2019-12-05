# csv-to-openml

A notebook to assist uploading a CSV file to [OpenML](https://openml.org).

OpenML requires uploaded datasets to have column annotations which CSV-files lack.
The notebook will infer column types with simple heuristics.
Afterwards, the user should verify the inferred types are correct, or correct them if needed.
Finally, the data is uploaded to OpenML, that's all it takes!

## Installation
 Make sure you have the requirements installed:
 
 `pip install -r requirements.txt`
 
 then launch Jupyter Notebook (`jupyter notebook`).
 This should open a new tab on your webbrowser, click the 'CSV to OpenML' notebook to open it.
 