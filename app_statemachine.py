# General Program Flow:
# Display Upload Widget
# > Upload CSV
# Display information on meta-data in OpenML
# Display data annotation widget
# > Annotate data
# Display Dublin Core annotation widget
# > Fill in form
# : Is API Key configured?
# If not > add API key
# Display Upload Widget
# Thanks!
from IPython.core.display import display, display_markdown, clear_output
import ipywidgets as widgets
import openml

from app_logic import csv_bytes_to_dataframe, create_openml_dataset, set_openml_apikey
from app_widgets import file_upload_widget, publish_button, DatasetAnnotation, data_annotation_widget_collection, \
    metadata_widget

COLUMN_ANNOTATION_TEXT = """
OpenML wants to capture some rich meta-data about uploaded datasets, so that other users and programs may make better use of the datasets.

It's crucial for OpenML to know the *type* of data in each column.
Each feature should be one of:

 - A numeric feature. Examples: `car price` or `tree height`
 - A string (text). Examples: `sales text` or `tree name`
 - A categorical feature (can only take one of a set of unique values). Examples: `car color` (red, blue, ...) or `evergreen` (yes, no).
 
Based on the data found in our csv file, we inferred the the types for each column.
Below you will find a table which allows you to add or edit any of the feature meta-data OpenML accepts:

In the **'Column Names'** column you will find the column names of your data.
You can edit the column names directly.

The **'Column Types'** column shows the column types as described above, as inferred from the data.
If the column type is not correct, please select the correct option from the dropdown menu.

The **'Example Values'** column simply shows some values of the column for easy reference.
This column should not be edited (editing it has no effect).

In the **'Ignore'** column, you can select the columns which should be ignored when creating models (e.g. identifiers or indexes).
If no such column exists in the dataset, this column may be ignored.

In the **'ID'** column you can select the column that contains row ids, if such a column is present.
If no row id column is present in the dataset, this column may be ignored.


Please check that the names and types are correct, complete the 'Ignore' and 'ID' columns
"""

# Main mechanic for showing elements:
#  - Display. Shows it below other displayed elements.
#  - Close. Removes the widget from display.
#  - clear_output. to remove everything from the output cell.


class App:
    """ Governs the flow of the csv-to-openml Jupyter Notebook App. """

    def __init__(self, dummy_mode: bool = False):
        self.data = None
        self.data_annotation = DatasetAnnotation()
        self._oml_dataset = None

        self._upload_csv = file_upload_widget
        self._publish_to_oml = publish_button
        self._metadata_widget = None
        self._column_annotation_widgets = None

        self._upload_csv.observe(self._on_file_uploaded, 'data')

        if dummy_mode:
            openml.config.start_using_configuration_for_example()

    def start(self):
        self.load_file_upload()

    def load_file_upload(self):
        clear_output()
        display_markdown("Please provide the CSV file you want to upload _to_ OpenML:", raw=True)
        display(self._upload_csv)

    def _on_file_uploaded(self, change):
        self.data = csv_bytes_to_dataframe(change['new'][0])
        self.load_column_annotation()

    def load_column_annotation(self):
        clear_output()
        display_markdown(COLUMN_ANNOTATION_TEXT, raw=True)
        self._column_annotation_widgets = data_annotation_widget_collection(self.data, self.data_annotation)
        display(self._column_annotation_widgets)

        next_button = widgets.Button(description='next')
        next_button.on_click(lambda _: self.load_metadata_form())
        display(next_button)

    def load_metadata_form(self):
        clear_output()
        display_markdown("Thanks for bearing with us! All this extra information is going to make sure the dataset is easier for others to find and understand. There's just a few more things we'd like to know:", raw=True)
        self._metadata_widget = metadata_widget(self.data_annotation)
        display(self._metadata_widget)

        def after_metadata(_):
            self._oml_dataset = create_openml_dataset(self.data, self.data_annotation)
            self.load_api_key_check()

        next_button = widgets.Button(description='next')
        next_button.on_click(after_metadata)
        display(next_button)

    def load_api_key_check(self):
        if openml.config.apikey != '':
            self.load_publish_to_openml()
            return

        # API Key field was empty, so it needs to be configured.
        clear_output()
        display_markdown(
            """ We noticed you have not configured an API key for OpenML yet.
                To find your API key, log in on the [OpenML website](https://openml.org) ([register](https://www.openml.org/register) if needed)
                , go to your account page (click the avatar image on the top right) and click "API Authentication". """,
            raw=True
        )

        def on_key_input_change(key):
            if set_openml_apikey(key):
                self.load_publish_to_openml()

        key_input = widgets.interactive(on_key_input_change, key='')
        key_input.kwargs_widgets[0].description = 'API Key:'
        display(key_input)

    def load_publish_to_openml(self):
        clear_output()

        def publish(_):
            self._oml_dataset.publish()
            display(self._oml_dataset)
            publish_button.disabled = True
            publish_button.description = 'Published!'

        publish_button.on_click(publish)
        display_markdown("That's it! By pressing the magical button below, your data will be uploaded to OpenML!",
                         raw=True)
        display(publish_button)







