from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.roles import set_classes
from docutils.parsers.rst.directives.tables import CSVTable
from docutils import nodes, statemachine
import io
import re
import csv
import json
import pathlib
from collections import OrderedDict
import requests


extension_json_current = None


class ExtensionList(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {'class': directives.class_option,
                   'name': directives.unchanged,
                   'list': directives.unchanged}

    def run(self):
        extension_list_name = self.options.pop('list', '')
        set_classes(self.options)

        admonition_node = nodes.admonition('', **self.options)
        self.add_name(admonition_node)

        title_text = self.arguments[0]

        textnodes, _ = self.state.inline_text(title_text,
                                              self.lineno)

        title = nodes.title(title_text, '', *textnodes)
        title.line = 0
        title.source = 'extension_list_' + extension_list_name
        admonition_node += title
        if 'classes' not in self.options:
            admonition_node['classes'] += ['admonition', 'note']

        admonition_node['classes'] += ['extension_list']
        admonition_node['ids'] += ['extensionlist-' + extension_list_name]

        definition_list = nodes.definition_list()
        definition_list.line = 0

        num = 0
        for num, extension in enumerate(extension_json_current['extensions']):
            if not extension.get('core'):
                continue
            category = extension.get('category')
            if extension_list_name and category != extension_list_name:
                continue

            name = extension['name']['en']
            description = extension['description']['en']

            some_term, _ = self.state.inline_text(name, self.lineno)

            some_def, _ = self.state.inline_text(description, self.lineno)

            link = nodes.reference(name, '', *some_term)
            path_split = pathlib.PurePath(self.state.document.attributes['source']).parts
            root_path = pathlib.PurePath(*[".." for x in range(0, len(path_split) - path_split.index('docs') - 1)])

            link['refuri'] = str(pathlib.PurePath(root_path, 'extensions', extension.get('slug', '')))
            link['translatable'] = True
            link.source = 'extension_list_' + extension_list_name
            link.line = num + 1

            term = nodes.term(name, '', link)

            definition_list += term

            text = nodes.paragraph(description, '', *some_def)
            text.source = 'extension_list_' + extension_list_name
            text.line = num + 1
            definition_list += nodes.definition(description, text)

        admonition_node += definition_list

        community = "The following are community extensions and are not maintained by Open Contracting Partnership."
        community_text, _ = self.state.inline_text(community, self.lineno)

        community_paragraph = nodes.paragraph(community, *community_text)
        community_paragraph['classes'] += ['hide']
        community_paragraph.source = 'extension_list_' + extension_list_name
        community_paragraph.line = num + 2

        admonition_node += community_paragraph

        return [admonition_node]


def format(text):
    return re.sub(r'\[([^\[]+)\]\(([^\)]+)\)', r'`\1 <\2>`__', text.replace("date-time", "[date-time](#date)"))


def gather_fields(json, path="", definition=""):
    properties = json.get('properties')
    if properties:
        for field_name, field_info in properties.items():
            if not field_info:
                continue
            yield from gather_fields(field_info, path + '/' + field_name, definition=definition)
            for key, value in field_info.items():
                if isinstance(value, dict):
                    yield from gather_fields(value, path + '/' + field_name, definition=definition)

            types = field_info.get('type', '')
            if isinstance(types, list):
                types = format(", ".join(types).replace(", null", "").replace("null,", ""))
            else:
                types = format(types)

            description = field_info.get("description")
            if description:
                yield [(path + '/' + field_name).lstrip("/"), definition, format(description), types]

    definitions = json.get('definitions')
    if definitions:
        for key, value in definitions.items():
            yield from gather_fields(value, definition=key)


def get_lines(headings, data):
    data.insert(0, headings)
    output = io.StringIO()
    writer = csv.writer(output)
    for line in data:
        writer.writerow(line)
    return output.getvalue().splitlines()


class AbstractExtensionTable(CSVTable):
    def parse_csv_data_into_rows(self, csv_data, dialect, source):
        # csv.py doesn't do Unicode; encode temporarily as UTF-8
        csv_reader = csv.reader([self.encode_for_csv(line + '\n')
                                 for line in csv_data], dialect=dialect)
        rows = []
        max_cols = 0
        for row_num, row in enumerate(csv_reader):
            row_data = []
            for cell_num, cell in enumerate(row):
                if row_num == 0 or cell_num not in self.cell_num_to_not_start_new_source:
                    new_source = source
                else:
                    new_source = ""
                # decode UTF-8 back to Unicode
                cell_text = self.decode_from_csv(cell)
                cell_data = (0, 0, 0, statemachine.StringList(
                    cell_text.splitlines(), source=new_source))
                row_data.append(cell_data)
            rows.append(row_data)
            max_cols = max(max_cols, len(row))
        return rows, max_cols


class ExtensionTable(AbstractExtensionTable):
    cell_num_to_not_start_new_source = (0, 3)

    option_spec = {'widths': directives.positive_int_list,
                   'extension': directives.unchanged,
                   'schema': directives.unchanged,
                   'ignore_path': directives.unchanged,
                   'definitions': directives.unchanged,
                   'exclude_definitions': directives.unchanged}

    def get_csv_data(self):
        valid_options = {'extension', 'ignore_path', 'definitions', 'exclude_definitions'}

        for option in self.options:
            if option not in valid_options:
                raise Exception('Unrecognized configuration {} in extensiontable directive'.format(option))

        extension = self.options.get('extension')
        ignore_path = self.options.get('ignore_path')
        definitions = self.options.get('definitions')
        exclude_definitions = self.options.get('exclude_definitions')

        if not extension:
            raise Exception("No extension configuration in extensiontable directive")
        if definitions and exclude_definitions:
            raise Exception("Only one of definitions or exclude_definitions must be set in extensiontable directive")

        headings = ["Field", "Definition", "Description", "Type"]

        if not extension_json_current['extensions']:
            return [",".join(headings)], "Extension {}".format(extension)

        for num, extension_obj in enumerate(extension_json_current['extensions']):
            if extension_obj['slug'] == extension:
                break
        else:
            raise Exception("Extension {} is not in the registry".format(extension))

        try:
            url = extension_obj['url'].rstrip('/') + '/' + 'release-schema.json'
            extension_patch = json.loads(requests.get(url).text, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError('{}: {}'.format(url, e.msg), e.doc, e.pos)

        data = []
        for row in gather_fields(extension_patch):
            data.append(row)

        if ignore_path:
            for row in data:
                row[0] = row[0].replace(ignore_path, "")

        if definitions:
            rows = []
            definitions = definitions.split()
            not_found = definitions[:]
            for row in data:
                if row[1] in definitions:
                    rows.append(row)
                if row[1] in not_found:
                    not_found.remove(row[1])
            if not_found:
                raise Exception("definitions not found: {}".format(', '.join(not_found)))
            data = rows

        if exclude_definitions:
            rows = []
            exclude_definitions = exclude_definitions.split()
            not_found = exclude_definitions[:]
            for row in data:
                if row[1] not in exclude_definitions:
                    rows.append(row)
                if row[1] in not_found:
                    not_found.remove(row[1])
            if not_found:
                raise Exception("exclude_definitions not found: {}".format(', '.join(not_found)))
            data = rows

        self.options['header-rows'] = 1

        return get_lines(headings, data), "Extension {}".format(extension)


class ExtensionSelectorTable(AbstractExtensionTable):
    cell_num_to_not_start_new_source = (3,)

    option_spec = {'group': directives.unchanged}

    def get_csv_data(self):
        data = []
        headings = ['', 'Extension', 'Description', 'Category', 'Extension URL']
        group = self.options.get('group')

        if group not in ('core', 'community'):
            raise Exception('Extension group must be either "core" or "community"')

        if group == 'core':
            extension_json = extension_json_current
            if not extension_json.get('extensions'):
                return [','.join(headings)], 'Extensions'

            for num, extension_obj in enumerate(extension_json['extensions']):
                if not extension_obj.get('core'):
                    continue
                extension_name = extension_obj['name'].get('en')
                extension_name = '{}::{}'.format(extension_name, extension_obj.get('documentation_url', ''))
                extension_description = extension_obj['description'].get('en')
                row = ['', extension_name, extension_description, extension_obj['category'],
                       '{}extension.json'.format(extension_obj['url'])]
                data.append(row)
        else:
            data = [['', '', '', '', '']]

        self.options['header-rows'] = 1
        self.options['class'] = ['extension-selector-table']
        self.options['widths'] = [8, 30, 42, 20, 0]

        return get_lines(headings, data), 'Extension registry'


def download_extensions(app, env, docnames):
    global extension_json_current
    extensions_current = 'http://standard.open-contracting.org/extension_registry/{}/extensions.json'.format(
        app.config.extension_registry_git_ref)
    try:
        extension_json_current = requests.get(extensions_current, timeout=1).json()
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        print("**********  Internet connection not found *************")
        extension_json_current = {"extensions": []}


def setup(app):
    app.connect('env-before-read-docs', download_extensions)
    app.add_config_value('extension_registry_git_ref', 'master', True)

    app.add_directive('extensionlist', ExtensionList)
    app.add_directive('extensiontable', ExtensionTable)
    app.add_directive('extensionselectortable', ExtensionSelectorTable)
