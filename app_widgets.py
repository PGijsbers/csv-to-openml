import numpy as np
import pandas as pd
from ipywidgets import widgets

upload_widget = widgets.FileUpload(
    accept='.csv',
    multiple=False,
    description='Select a csv file'
)

publish_button = widgets.Button(
    description='Publish dataset',
    disabled=True,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click me',
    icon='check',
    visible=False
)


class DatasetAnnotation:
    """ A Dataclass for referencing dataset meta-data. """

    def __init__(self):
        self.ignore_columns = []
        self.id_column = None
        self.target_column = None

        self.name = None
        self.description = None
        self.collection_date = None
        self.creator = None
        self.contributor = None
        self.dataset_url = None
        self.paper_url = None
        self.citation = None
        self.licence = None
        self.language = None

    def update_column_name(self, old: str, new: str):
        if old in self.ignore_columns:
            self.ignore_columns.remove(old)
            self.ignore_columns.append(new)

        if old == self.id_column:
            self.id_column = new

        if old == self.target_column:
            self.target_column = new


def data_annotation_widget_collection(data: pd.DataFrame, annotation: DatasetAnnotation) -> widgets.VBox:
    """ Creates a collection of widgets to help annotate the data columns.
    The `data` DataFrame, `target_column`, `id_column`
    """
    id_radio_buttons = []
    target_radio_buttons = []

    def set_ignore_column_maker(column_widget):
        def ignore_column(change):
            if change['new']:
                annotation.ignore_columns.append(column_widget.value)
            else:
                annotation.ignore_columns.remove(column_widget.value)

        return ignore_column

    def set_radio_button_active(active_button, group):
        """ Sets `active_button` to be the only active radio button in the group. """
        for button in group:
            if active_button != button:
                button.value = None

    def set_id_column_maker(column_widget):
        def set_id_column(change):
            if change['new'] == '':
                annotation.id_column = column_widget.value
                set_radio_button_active(change['owner'], id_radio_buttons)

        return set_id_column

    def set_target_column_maker(column_widget):
        def set_target_column(change):
            if change['new'] == '':
                annotation.target_column = column_widget.value
                set_radio_button_active(change['owner'], target_radio_buttons)

        return set_target_column

    def set_column_type_maker(column_widget):
        def set_column_type(change):
            if change['new'] == 'categorical':
                data[column_widget.value] = data[column_widget.value].astype('category')
            if change['new'] == 'numeric':
                data[column_widget.value] = pd.to_numeric(data[column_widget.value])
            if change['new'] == 'string':
                data[column_widget.value] = data[column_widget.value].astype('str')

        return set_column_type

    w_col_name, w_col_type, w_col_examples, w_ignore, w_id = '200px', '150px', '300px', '60px', '40px'
    column_names_and_width = [
        ('Column Names', '200px'),
        ('Column Types', '150px'),
        ('Example Values', '300px'),
        ('Ignore', '60px'),
        ('ID', '40px'),
        ('Target', '60px')
    ]
    column_labels = [widgets.Label(name, layout=widgets.Layout(width=width))
                     for (name, width) in column_names_and_width]
    coltype_widgets = [widgets.HBox(column_labels)]

    for i, column in enumerate(data.columns):
        column_name_widget = widgets.Text(
            value=column,
            layout=widgets.Layout(width=w_col_name)
        )

        def set_column_name(change):
            data.rename(columns={change['old']: change['new']}, inplace=True)
            # Update Ignore dict and ID field to refer to the new column name
            annotation.update_column_name(change['old'], change['new'])

        column_name_widget.observe(set_column_name, 'value')

        if data[column].dtype.name == 'category':
            coltype = 'categorical'
        elif np.issubdtype(data[column].dtype, np.number):
            coltype = 'numeric'
        else:
            coltype = 'string'

        column_type_widget = widgets.Dropdown(
            options=['numeric', 'string', 'categorical'],
            value=coltype,
            layout=widgets.Layout(width=w_col_type)
        )
        set_column_type = set_column_type_maker(column_name_widget)
        column_type_widget.observe(set_column_type, 'value')

        example_values_widget = widgets.Text(
            value=', '.join([str(v) for v in data[column].head().values]),
            layout=widgets.Layout(width=w_col_examples)
        )

        ignore_widget = widgets.Checkbox(value=False,
                                         layout=widgets.Layout(width=w_ignore),
                                         style={'description_width': '0px'})
        set_ignore_column = set_ignore_column_maker(column_name_widget)
        ignore_widget.observe(set_ignore_column, 'value')

        id_widget = widgets.RadioButtons(options=[''],
                                         value=None,
                                         layout=widgets.Layout(width=w_id),
                                         style={'description_width': '0px'})
        set_id_column = set_id_column_maker(column_name_widget)
        id_widget.observe(set_id_column, 'value')
        id_radio_buttons.append(id_widget)

        target_widget = widgets.RadioButtons(options=[''],
                                             value=None,
                                             layout=widgets.Layout(width=w_id),
                                             style={'description_width': '0px'})
        set_target_column = set_target_column_maker(column_name_widget)
        target_widget.observe(set_target_column, 'value')
        target_radio_buttons.append(target_widget)

        coltype_widgets.append(
            widgets.HBox(
                [
                    column_name_widget,
                    column_type_widget,
                    example_values_widget,
                    ignore_widget,
                    id_widget,
                    target_widget
                ])
        )

    return widgets.VBox(coltype_widgets)


def metadata_widget(annotation: DatasetAnnotation) -> widgets.VBox:
    """ Creates a form with input fields for metadata, such as title and description of a dataset.

     The form input is linked to the annotation object.

     """
    def create_widget(label: str, long_description: str, type_, layout_args=None):
        layout_args = dict(width='900px') if layout_args is None else layout_args
        field = label.replace(' ', '_').lower()
        if '(' in field:
            field = field[:field.index('(')]

        widget = type_(
            value=None,
            placeholder=long_description,
            description=label,
            long_description=long_description,
            layout=widgets.Layout(**layout_args)
        )

        def update(change):
            setattr(annotation, field, change['new'])
        widget.observe(update, 'value')
        return widget

    name_widget = create_widget('Name', 'Name of the dataset', widgets.Text)

    desc_long = (
        'A description of the dataset. '
        'Include for example:\n'
        ' - What is the domain of this dataset?\n'
        ' - How was the dataset gathered?\n'
        ' - What is the meaning of each feature?'
    )
    description_widget = create_widget(
        'Description', desc_long, widgets.Textarea,
        dict(width='900px', height='120px')
    )

    collection_date_widget = create_widget('Collection Date', 'Date data was originally collected', widgets.DatePicker)
    creator_widget = create_widget('Creator(s)', 'Original creator(s) of the dataset', widgets.Text)
    contributor_widget = create_widget('Contributor(s)',
                                       'People who further contributed to the dataset (e.g. formatting)', widgets.Text)
    dataset_url_widget = create_widget('Data URL', 'URL to the dataset if it is also hosted elsewhere', widgets.Text)
    paper_url_widget = create_widget('Paper URL', 'URL to the paper which introduced the dataset', widgets.Text)
    citation_widget = create_widget('Citation', 'Citation for inclusion in a bibliography', widgets.Text)
    # https://help.data.world/hc/en-us/articles/115006114287-Common-license-types-for-datasets
    licence_widget = create_widget('Licence', 'Licence of the dataset, e.g. Public Domain, CC0, CC BY-NC', widgets.Text)
    language_widget = create_widget('Language(s)', 'Language(s) in which the data is represented.', widgets.Text)

    return widgets.VBox([
        name_widget, description_widget, creator_widget, contributor_widget, collection_date_widget,
        dataset_url_widget, paper_url_widget, citation_widget, licence_widget, language_widget
    ])
