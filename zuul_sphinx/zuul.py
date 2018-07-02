# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import OrderedDict
import codecs
import os

from sphinx import addnodes
from docutils.parsers.rst import Directive
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from docutils import nodes

import yaml


class ZuulSafeLoader(yaml.SafeLoader):

    def __init__(self, *args, **kwargs):
        super(ZuulSafeLoader, self).__init__(*args, **kwargs)
        self.add_multi_constructor('!encrypted/', self.construct_encrypted)

    @classmethod
    def construct_encrypted(cls, loader, tag_suffix, node):
        return loader.construct_sequence(node)


class ProjectTemplate(object):
    def __init__(self, conf):
        self.name = conf['name']
        self.description = conf.get('description', '')
        self.pipelines = OrderedDict()
        self.parse(conf)

    def parse(self, conf):
        for k in sorted(conf.keys()):
            v = conf[k]
            if not isinstance(v, dict):
                continue
            if 'jobs' not in v:
                continue
            jobs = []
            for job in v['jobs']:
                if isinstance(job, dict):
                    job = list(job.keys())[0]
                jobs.append(job)
            if jobs:
                self.pipelines[k] = jobs


class Layout(object):
    def __init__(self):
        self.jobs = []
        self.project_templates = []


class ZuulDirective(Directive):
    has_content = True

    def find_zuul_yaml(self):
        root = self.state.document.settings.env.relfn2path('.')[1]
        while root:
            for fn in ['zuul.yaml', '.zuul.yaml', 'zuul.d', '.zuul.d']:
                path = os.path.join(root, fn)
                if os.path.exists(path):
                    return path
            root = os.path.split(root)[0]
        raise Exception(
            "Unable to find zuul config in zuul.yaml, .zuul.yaml,"
            " zuul.d or .zuul.d")

    def parse_zuul_yaml(self, path):
        with open(path) as f:
            data = yaml.load(f, Loader=ZuulSafeLoader)
        layout = Layout()
        for obj in data:
            if 'job' in obj:
                layout.jobs.append(obj['job'])
            if 'project-template' in obj:
                layout.project_templates.append(
                    ProjectTemplate(obj['project-template']))
        return layout

    def parse_zuul_d(self, path):
        layout = Layout()
        for conf in os.listdir(path):
            with open(os.path.join(path, conf)) as f:
                data = yaml.load(f, Loader=ZuulSafeLoader)
            for obj in data:
                if 'job' in obj:
                    layout.jobs.append(obj['job'])
                if 'project-template' in obj:
                    layout.project_templates.append(
                        ProjectTemplate(obj['project-template']))
        return layout

    def _parse_zuul_layout(self):
        env = self.state.document.settings.env
        if not env.domaindata['zuul']['layout']:
            path = self.find_zuul_yaml()
            if path.endswith('zuul.d'):
                layout = self.parse_zuul_d(path)
            else:
                layout = self.parse_zuul_yaml(path)
            env.domaindata['zuul']['layout_path'] = path
            env.domaindata['zuul']['layout'] = layout

    @property
    def zuul_layout(self):
        self._parse_zuul_layout()
        env = self.state.document.settings.env
        return env.domaindata['zuul']['layout']

    @property
    def zuul_layout_path(self):
        self._parse_zuul_layout()
        env = self.state.document.settings.env
        return env.domaindata['zuul']['layout_path']

    def generate_zuul_job_content(self, name):
        lines = []
        for job in self.zuul_layout.jobs:
            if job['name'] == name:
                lines.append('.. zuul:job:: %s' % name)
                if 'branches' in job:
                    branches = job['branches']
                    if not isinstance(branches, list):
                        branches = [branches]
                    variant = ', '.join(branches)
                    lines.append('   :variant: %s' % variant)
                lines.append('')
                for l in job.get('description', '').split('\n'):
                    lines.append('   ' + l)
                lines.append('')
        return lines

    def generate_zuul_project_template_content(self, name):
        lines = []
        for template in self.zuul_layout.project_templates:
            if template.name == name:
                lines.append('.. zuul:project_template:: %s' % name)
                lines.append('')
                for l in template.description.split('\n'):
                    lines.append('   ' + l)
                for pipeline, jobs in template.pipelines.items():
                    lines.append('')
                    lines.append('   **'+pipeline+'**')
                    for job in jobs:
                        lines.append('      * :zuul:xjob:`' + job + '`')
                lines.append('')
        return lines

    def find_zuul_roles(self):
        root = os.path.dirname(self.zuul_layout_path)
        roledir = os.path.join(root, 'roles')
        env = self.state.document.settings.env
        roles = env.domaindata['zuul']['role_paths']
        for p in os.listdir(roledir):
            role_readme = os.path.join(roledir, p, 'README.rst')
            if os.path.exists(role_readme):
                roles[p] = role_readme

    @property
    def zuul_role_paths(self):
        env = self.state.document.settings.env
        roles = env.domaindata['zuul']['role_paths']
        if roles is None:
            roles = {}
            env.domaindata['zuul']['role_paths'] = roles
            self.find_zuul_roles()
        return roles

    def generate_zuul_role_content(self, name):
        lines = []
        lines.append('.. zuul:role:: %s' % name)
        lines.append('')
        role_readme = self.zuul_role_paths[name]
        with codecs.open(role_readme, encoding='utf-8') as f:
            role_lines = f.read().split('\n')
            for l in role_lines:
                lines.append('   ' + l)
        return lines


class ZuulObjectDescription(ZuulDirective, ObjectDescription):
    object_names = {
        'attr': 'attribute',
        'var': 'variable',
        'jobvar': 'job variable',
        'rolevar': 'role variable',
    }

    def get_path(self):
        return self.env.ref_context.get('zuul:attr_path', [])

    def get_display_path(self):
        return self.env.ref_context.get('zuul:display_attr_path', [])

    @property
    def parent_pathname(self):
        return '.'.join(self.get_display_path())

    @property
    def full_pathname(self):
        name = self.names[-1].lower()
        return '.'.join(self.get_path() + [name])

    def add_target_and_index(self, name, sig, signode):
        targetname = self.objtype + '-' + self.full_pathname
        if targetname not in self.state.document.ids:
            signode['names'].append(targetname)
            signode['ids'].append(targetname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['zuul']['objects']
            if targetname in objects:
                self.state_machine.reporter.warning(
                    'duplicate object description of %s, ' % targetname +
                    'other instance in ' +
                    self.env.doc2path(objects[targetname][0]) +
                    ', use :noindex: for one of them',
                    line=self.lineno)
            objects[targetname] = (self.env.docname, self.objtype)

        objname = self.object_names.get(self.objtype, self.objtype)
        if self.parent_pathname:
            indextext = '%s (%s of %s)' % (name, objname,
                                           self.parent_pathname)
        else:
            indextext = '%s (%s)' % (name, objname)
        self.indexnode['entries'].append(('single', indextext,
                                          targetname, '', None))


######################################################################
#
# Object description directives
#

class ZuulJobDirective(ZuulObjectDescription):
    option_spec = {
        'variant': lambda x: x,
    }

    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        element = self.names[-1]
        path.append(element)

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig


class ZuulProjectTemplateDirective(ZuulObjectDescription):
    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        element = self.names[-1]
        path.append(element)

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig


class ZuulRoleDirective(ZuulObjectDescription):
    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        element = self.names[-1]
        path.append(element)

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig


class ZuulAttrDirective(ZuulObjectDescription):
    has_content = True

    option_spec = {
        'required': lambda x: x,
        'default': lambda x: x,
        'noindex': lambda x: x,
    }

    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        path.append(self.names[-1])
        path = self.env.ref_context.setdefault('zuul:display_attr_path', [])
        path.append(self.names[-1])

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()
        path = self.env.ref_context.get('zuul:display_attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        path = self.get_display_path()
        signode['is_multiline'] = True
        line = addnodes.desc_signature_line()
        line['add_permalink'] = True
        for x in path:
            line += addnodes.desc_addname(x + '.', x + '.')
        line += addnodes.desc_name(sig, sig)
        if 'required' in self.options:
            line += addnodes.desc_annotation(' (required)', ' (required)')
        signode += line
        if 'default' in self.options:
            line = addnodes.desc_signature_line()
            line += addnodes.desc_type('Default: ', 'Default: ')
            line += nodes.literal(self.options['default'],
                                  self.options['default'])
            signode += line
        return sig


class ZuulValueDirective(ZuulObjectDescription):
    has_content = True

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(sig, sig)
        return sig


class ZuulVarDirective(ZuulObjectDescription):
    has_content = True

    option_spec = {
        'type': lambda x: x,
        'default': lambda x: x,
        'hidden': lambda x: x,
        'noindex': lambda x: x,
    }

    type_map = {
        'list': '[]',
        'dict': '{}',
    }

    def get_type_str(self):
        if 'type' in self.options:
            return self.type_map[self.options['type']]
        return ''

    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        element = self.names[-1]
        path.append(element)
        path = self.env.ref_context.setdefault('zuul:display_attr_path', [])
        element = self.names[-1] + self.get_type_str()
        path.append(element)

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()
        path = self.env.ref_context.get('zuul:display_attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        if 'hidden' in self.options:
            return sig
        path = self.get_display_path()
        signode['is_multiline'] = True
        line = addnodes.desc_signature_line()
        line['add_permalink'] = True
        for x in path:
            line += addnodes.desc_addname(x + '.', x + '.')
        line += addnodes.desc_name(sig, sig)
        if 'required' in self.options:
            line += addnodes.desc_annotation(' (required)', ' (required)')
        signode += line
        if 'default' in self.options:
            line = addnodes.desc_signature_line()
            line += addnodes.desc_type('Default: ', 'Default: ')
            line += nodes.literal(self.options['default'],
                                  self.options['default'])
            signode += line
        return sig


class ZuulJobVarDirective(ZuulVarDirective):
    pass


class ZuulRoleVarDirective(ZuulVarDirective):
    pass


class ZuulStatDirective(ZuulObjectDescription):
    has_content = True

    option_spec = {
        'type': lambda x: x,
        'hidden': lambda x: x,
        'noindex': lambda x: x,
    }

    def before_content(self):
        path = self.env.ref_context.setdefault('zuul:attr_path', [])
        element = self.names[-1]
        path.append(element)
        path = self.env.ref_context.setdefault('zuul:display_attr_path', [])
        element = self.names[-1]
        path.append(element)

    def after_content(self):
        path = self.env.ref_context.get('zuul:attr_path')
        if path:
            path.pop()
        path = self.env.ref_context.get('zuul:display_attr_path')
        if path:
            path.pop()

    def handle_signature(self, sig, signode):
        if 'hidden' in self.options:
            return sig
        path = self.get_display_path()
        for x in path:
            signode += addnodes.desc_addname(x + '.', x + '.')
        signode += addnodes.desc_name(sig, sig)
        if 'type' in self.options:
            t = ' (%s)' % self.options['type']
            signode += addnodes.desc_annotation(t, t)
        return sig


######################################################################
#
# Autodoc directives
#

class ZuulAutoJobDirective(ZuulDirective):
    def run(self):
        name = self.content[0]
        lines = self.generate_zuul_job_content(name)
        self.state_machine.insert_input(lines, self.zuul_layout_path)
        return []


class ZuulAutoJobsDirective(ZuulDirective):
    has_content = False

    def run(self):
        lines = []
        names = set()
        for job in self.zuul_layout.jobs:
            name = job['name']
            if name in names:
                continue
            lines.extend(self.generate_zuul_job_content(name))
            names.add(name)
        self.state_machine.insert_input(lines, self.zuul_layout_path)
        return []

class ZuulAutoProjectTemplateDirective(ZuulDirective):
    def run(self):
        name = self.content[0]
        lines = self.generate_zuul_project_template_content(name)
        self.state_machine.insert_input(lines, self.zuul_layout_path)
        return []


class ZuulAutoProjectTemplatesDirective(ZuulDirective):
    has_content = False

    def run(self):
        lines = []
        names = set()
        for template in self.zuul_layout.project_templates:
            name = template.name
            if name in names:
                continue
            lines.extend(self.generate_zuul_project_template_content(name))
            names.add(name)
        self.state_machine.insert_input(lines, self.zuul_layout_path)
        return []


class ZuulAutoRoleDirective(ZuulDirective):
    def run(self):
        name = self.content[0]
        lines = self.generate_zuul_role_content(name)
        self.state_machine.insert_input(lines, self.zuul_role_paths[name])
        return []


class ZuulAutoRolesDirective(ZuulDirective):
    has_content = False

    def run(self):
        role_names = reversed(sorted(self.zuul_role_paths.keys()))
        for name in role_names:
            lines = self.generate_zuul_role_content(name)
            self.state_machine.insert_input(lines, self.zuul_role_paths[name])
        return []


class ZuulAbbreviatedXRefRole(XRefRole):

    def process_link(self, env, refnode, has_explicit_title, title,
                     target):
        title, target = super(ZuulAbbreviatedXRefRole, self).process_link(
            env, refnode, has_explicit_title, title, target)
        if not has_explicit_title:
            title = title.split('.')[-1]
        return title, target


class ZuulDomain(Domain):
    name = 'zuul'
    label = 'Zuul'

    directives = {
        # Object description directives
        'job': ZuulJobDirective,
        'project_template': ZuulProjectTemplateDirective,
        'role': ZuulRoleDirective,
        'attr': ZuulAttrDirective,
        'value': ZuulValueDirective,
        'var': ZuulVarDirective,
        'stat': ZuulStatDirective,
        'jobvar': ZuulJobVarDirective,
        'rolevar': ZuulRoleVarDirective,
        # Autodoc directives
        'autojob': ZuulAutoJobDirective,
        'autojobs': ZuulAutoJobsDirective,
        'autoproject_template': ZuulAutoProjectTemplateDirective,
        'autoproject_templates': ZuulAutoProjectTemplatesDirective,
        'autorole': ZuulAutoRoleDirective,
        'autoroles': ZuulAutoRolesDirective,
    }

    roles = {
        'job': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                        warn_dangling=True),
        'xjob': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                         warn_dangling=False),
        'project_template':
            XRefRole(innernodeclass=nodes.inline,  # type: ignore
                     warn_dangling=True),
        'role': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                         warn_dangling=True),
        'attr': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                         warn_dangling=True),
        'value': ZuulAbbreviatedXRefRole(
            innernodeclass=nodes.inline,  # type: ignore
            warn_dangling=True),
        'var': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                        warn_dangling=True),
        'stat': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                         warn_dangling=True),
        'jobvar': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                           warn_dangling=True),
        'rolevar': XRefRole(innernodeclass=nodes.inline,  # type: ignore
                            warn_dangling=True),
    }

    initial_data = {
        'layout': None,
        'layout_path': None,
        'role_paths': None,
        'objects': {},
    }  # type: Dict[str, Dict]

    def resolve_xref(self, env, fromdocname, builder, type, target,
                     node, contnode):
        objects = self.data['objects']
        if type == 'xjob':
            type = 'job'
        name = type + '-' + target
        obj = objects.get(name)
        if obj:
            return make_refnode(builder, fromdocname, obj[0], name,
                                contnode, name)

    def clear_doc(self, docname):
        for fullname, (fn, _l) in list(self.data['objects'].items()):
            if fn == docname:
                del self.data['objects'][fullname]


def setup(app):
    app.add_domain(ZuulDomain)
