import csv
import json
import os
from functools import lru_cache

import jsonpointer
import requests
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import set_classes
from myst_parser.main import to_docutils
from ocdsextensionregistry import ExtensionRegistry

live_branch = os.getenv('TRAVIS_BRANCH', os.getenv('GITHUB_REF', '').rsplit('/', 1)[-1]) in {'1.0', '1.1', 'latest'}
extensions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/main/extensions.csv'
extension_versions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/main/extension_versions.csv'  # noqa: E501
extension_explorer_template = 'https://extensions.open-contracting.org/{}/extensions/{}/{}/'


@lru_cache()
def get_extension_explorer_extensions_json():
    return requests.get('https://extensions.open-contracting.org/extensions.json').json()


class FieldDescription(Directive):
    required_arguments = 2

    def run(self):
        filename = self.arguments[0]
        pointer = self.arguments[1]

        env = self.state.document.settings.env
        path = os.path.join(os.path.dirname(env.doc2path(env.docname)), filename)
        env.note_dependency(path)

        try:
            with open(path, encoding='utf-8') as f:
                schema = json.load(f)
                description = jsonpointer.resolve_pointer(schema, f'{pointer}/description')
        except FileNotFoundError:
            raise self.error(f'JSON Schema file not found: {path}')
        except PermissionError:
            raise self.error(f'JSON Schema file not readable: {path}')
        except json.decoder.JSONDecodeError:
            raise self.error(f'JSON Schema file not valid: {path}')
        except jsonpointer.JsonPointerException:
            raise self.error(f"Pointer '{pointer}/description' not found: {path}")

        block_quote = nodes.block_quote('', *to_docutils(description).children,
                                        classes=['directive--field-description'])

        return [block_quote]


class CodeDescription(Directive):
    required_arguments = 2

    def run(self):
        config = self.state.document.settings.env.config
        language = config.overrides.get('language', 'en')
        try:
            headers = config.codelist_headers[language]
        except KeyError:
            raise self.error(f"codelist_headers in conf.py is missing a '{language}' key")

        filename = self.arguments[0]
        code = self.arguments[1]

        env = self.state.document.settings.env
        path = os.path.join(os.path.dirname(env.doc2path(env.docname)), filename)
        env.note_dependency(path)

        try:
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                description = next(row[headers['description']] for row in reader if row[headers['code']] == code)
        except FileNotFoundError:
            raise self.error(f'CSV codelist file not found: {path}')
        except PermissionError:
            raise self.error(f'CSV codelist file not readable: {path}')
        except KeyError as e:
            raise self.error(f"Column {e} not found ({', '.join(reader.fieldnames)}): {path}")
        except StopIteration:
            raise self.error(f"Value '{code}' not found in column '{headers['code']}': {path}")

        block_quote = nodes.block_quote('', *to_docutils(description).children,
                                        classes=['directive--code-description'])

        return [block_quote]


class ExtensionExplorerLinkList(Directive):
    def run(self):
        config = self.state.document.settings.env.config
        extension_versions = config.extension_versions
        language = config.overrides.get('language', 'en')

        items = []
        extensions = get_extension_explorer_extensions_json()

        for identifier, version in extension_versions.items():
            name = extensions[identifier]['versions'][version]['metadata']['name']
            if language not in name:
                language = 'en'

            url = extension_explorer_template.format(language, identifier, version)

            text = name[language]
            if version != 'master':
                text += ' ({})'.format(version)

            reference = nodes.reference('', text, refuri=url)
            paragraph = nodes.paragraph('', '', reference)
            item = nodes.list_item('', paragraph)
            items.append(item)

        return [nodes.bullet_list('', *items)]


class ExtensionList(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {'class': directives.class_option,
                   'name': directives.unchanged,
                   'list': directives.unchanged}

    def run(self):
        config = self.state.document.settings.env.config
        extension_versions = config.extension_versions
        language = config.overrides.get('language', 'en')

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

        # Only list core extensions whose version matches the version specified in `conf.py` and whose category matches
        # the category specified by the directive's `list` option.

        registry = ExtensionRegistry(extension_versions_url, extensions_url)

        num = 0
        for identifier, version in extension_versions.items():
            extension = registry.get(id=identifier, core=True, version=version)
            if extension_list_name and extension.category != extension_list_name:
                continue

            # Avoid "403 Client Error: rate limit exceeded for url" on development branches.
            try:
                metadata = extension.metadata
            except requests.exceptions.HTTPError:
                if live_branch:
                    raise
                metadata = {'name': {'en': identifier}, 'description': {'en': identifier}}

            name = metadata['name']['en']
            description = metadata['description']['en']

            some_term, _ = self.state.inline_text(name, self.lineno)
            some_def, _ = self.state.inline_text(description, self.lineno)

            link = nodes.reference(name, '', *some_term)
            link['refuri'] = extension_explorer_template.format(language, identifier, version)
            link['translatable'] = True
            link.source = 'extension_list_' + extension_list_name
            link.line = num + 1

            term = nodes.term(name, '', link)

            definition_list += term

            text = nodes.paragraph(description, '', *some_def)
            text.source = 'extension_list_' + extension_list_name
            text.line = num + 1
            definition_list += nodes.definition(description, text)

        if extension_list_name and not registry.filter(category=extension_list_name):
            raise self.warning('No extensions have category {} in extensionlist directive'.format(extension_list_name))

        admonition_node += definition_list

        community = "The following are community extensions and are not maintained by Open Contracting Partnership."
        community_text, _ = self.state.inline_text(community, self.lineno)

        community_paragraph = nodes.paragraph(community, *community_text)
        community_paragraph['classes'] += ['hide']
        community_paragraph.source = 'extension_list_' + extension_list_name
        community_paragraph.line = num + 2

        admonition_node += community_paragraph

        return [admonition_node]


def setup(app):
    app.add_directive('field-description', FieldDescription)
    app.add_directive('code-description', CodeDescription)
    app.add_directive('extensionexplorerlinklist', ExtensionExplorerLinkList)
    app.add_directive('extensionlist', ExtensionList)

    app.add_config_value('extension_versions', {}, True)
    app.add_config_value('codelist_headers', {
        'en': {'code': 'Code', 'description': 'Description'},
        'es': {'code': 'Código', 'description': 'Descripción'},
        'fr': {'code': 'Code', 'description': 'Description'},
        'it': {'code': 'Codice', 'description': 'Descrizione'},
    }, True)
