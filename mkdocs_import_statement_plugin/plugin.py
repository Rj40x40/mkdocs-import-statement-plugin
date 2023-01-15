#!/usr/bin/env python

"""
Support @import statement for MkDocs.

@import statement is supported in Markdown Preview Enhanced (hereafter
 referred to as MPE), that is very popular extension for Atom and
 Visual Studio Code.

The explanation of @import statement is describe in following page.

https://shd101wyy.github.io/markdown-preview-enhanced/#/file-imports


Here are the supported file types in this plugin as similar as MPE.

.jpeg(.jpg), .gif, .png, .apng, .svg, .bmp file will be treated as markdown
 image.
.csv file will be converted to markdown table.
.js file will be included as <script src="your_js"></script>.
.md, .html(.htm) file wil be embedded directly.
.mermaid file will be rendered by mermaid.
.dot file will be rendered by viz.js (graphviz).
.plantuml(.puml) file will be rendered by PlantUML.
"""

import os
import re
import csv


from mkdocs.plugins import BasePlugin


def debug_msg(str):
    bVerbose = False
    # bVerbose = True
    if bVerbose:
        print(str)


class cd:
    """
    Context manager for changing the current working directory
    Credits: https://stackoverflow.com/a/13197763/5525118
    """

    def __init__(self, newPath):
        if len(newPath) > 0:
            self.newPath = os.path.expanduser(newPath)
        else:
            self.newPath = None

    def __enter__(self):
        self.savedPath = os.getcwd()
        if self.newPath is not None:
            debug_msg('cd.__enter__("{}")'.format(self.newPath))
            os.chdir(self.newPath)
        else:
            debug_msg('cd.__enter__(None)')

    def __exit__(self, etype, value, traceback):
        debug_msg('cd.__exit__("{}")'.format(self.savedPath))
        os.chdir(self.savedPath)


class ImportPlugin(BasePlugin):
    # def on_pre_build(self, config):
    #     print('Hello World!')

    def on_page_markdown(self, markdown, page, config, files, **kwargs):
        """
        from https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown

          The page_markdown event is called after the page's markdown is
        loaded from file and can be used to alter the Markdown source text.
          The meta- data has been stripped off and is available as page.meta
        at this point.

        Parameters:
            markdown (str): Markdown source text of page as string
            page (Page): mkdocs.nav.Page instance
            config (MkDocsConfig): global configuration object
            files (Files): global files collection
        Returns:
            Optional[str]: Markdown source text of page as string
        """
        mkdocs_dir = "docs"
        if self.config.get("base_path") == "config_dir":
            mkdocs_dir = config["config_file_path"]
        if self.config.get("base_path") == "docs_dir":
            mkdocs_dir = config["docs_dir"]

        with cd(mkdocs_dir):
            self.mkdocs_dir = os.getcwd()
            self.ext_func = {
                ".jpeg": self.import_image,
                ".jpg": self.import_image,
                ".gif": self.import_image,
                ".png": self.import_image,
                ".apng": self.import_image,
                ".svg": self.import_image,
                ".bmp": self.import_image,
                ".js": self.import_javascript,
                ".csv": self.import_table,
                ".md": self.import_markdown,
                ".html": self.import_text,
                ".htm": self.import_text,
                ".mermaid": self.import_comment_mermaid,
                ".dot": self.import_comment_dot,
                # ".plantuml": self.import_comment_plantuml,
                ".puml": self.import_comment_plantuml,
                ".pu": self.import_comment_plantuml
            }
            fmt = 'on_page_markdown(), mkdocs_dir = "{}"'
            debug_msg(fmt.format(self.mkdocs_dir))
            input = markdown.split('\n')
            output = self.process_foreach(input)
            return '\n'.join(output)

        # should not be called here
        return markdown

    def process_foreach(self, src):
        """
        @import statement in src is replaced with processed text.
        """
        # language = None
        output = []
        comment_block = None
        for row in src:
            line = row.rstrip()
            if line.startswith('```'):
                if comment_block is None:
                    # Comment starts from current line.
                    comment_block = [line]
                else:
                    # Comment ends at current line.
                    comment_block.append(line)
                    output.extend(comment_block)
                    comment_block = None
                continue

            if comment_block is not None:
                # Now in a comment block
                comment_block.append(line)
                continue

            # Current line is body.

            # Check @import statement
            importMatch = re.match(r'^(\s*)@import(\s+)\"([^\"]+)\";?', line)
            if importMatch is None:
                # Current line is not @import statement.
                output.append(line)
                continue

            # Check option
            option = None
            leftParen = line.find("{")
            if leftParen > 0:
                rightParen = line.find("}")
                if leftParen < rightParen:
                    option = line.substring(leftParen + 1, rightParen)

            # Current line is @import statement.
            block = self.process_import_line(importMatch.group(3), option)
            if block is None:
                # the line is not processed, so use the original line.
                output.append(line)
            else:
                output.extend(block)

        # All lines are processed

        # Append comment block if still exists.
        if comment_block is not None:
            output.extend(comment_block)

        return output

    def process_import_line(self, path, option=None):
        """
        Process @import line depends on the file extension.
        """
        debug_msg('Start process_import_line("{}").'.format(path))
        if not os.path.exists(path):
            raise FileNotFoundError(
                "[import-statement-plugin]: File does not exist: %s" % path
            )

        # Check extension
        words = os.path.splitext(path)
        extname = words[1].lower()

        if extname in self.ext_func:
            return self.ext_func[extname](path, option)

        # Unknown file extension
        return None  # No process

    # type dependency process lines

    def import_comment(self, path, comment_type):
        output = ["```" + comment_type]
        output.extend(self.import_text(path))
        output.append("```")
        return output

    def import_comment_mermaid(self, path, option=None):
        return self.import_comment(path, "mermaid")

    def import_comment_dot(self, path, option=None):
        return self.import_comment(path, "dot")

    def import_comment_plantuml(self, path, option=None):
        return self.import_comment(path, "plantuml")

    def import_image(self, path, option=None):
        if os.path.isabs(path):
            abspath = path
        else:
            abspath = os.path.abspath(path)

        debug_msg('import_image(), image abspath = "{}"'.format(abspath))
        relpath = os.path.relpath(abspath, self.mkdocs_dir)
        debug_msg('import_image(), image relpath = "{}"'.format(relpath))
        if option is None:
            line = "![]({})".format(relpath)
        else:
            line = '<img src="{}" {}>'.format(relpath, option)
        debug_msg('import_image(), image output = "{}"'.format(line))
        return [line]

    def import_script(self, path, texttype, option=None):
        if os.path.isabs(path):
            abspath = path
        else:
            abspath = os.path.abspath(path)

        debug_msg('import_script(), image abspath = "{}"'.format(abspath))
        relpath = os.path.relpath(abspath, self.mkdocs_dir)
        debug_msg('import_script(), image relpath = "{}"'.format(relpath))
        if texttype is None:
            fmt = '<script src="{}"></script>'
        else:
            fmt = '<script type="text/' + texttype + '" src="{}"></script>'

        line = fmt.format(relpath)
        debug_msg('import_script(), image output = "{}"'.format(line))
        return [line]

    def import_javascript(self, path, option=None):
        debug_msg('import_javascript("{}")'.format(path))
        return self.import_script(path, "javascript", option)

    def import_markdown(self, path, option=None):
        debug_msg('import_markdown("{}")'.format(path))
        with open(path, 'r') as f:
            dirname = os.path.dirname(path)
            if dirname is None:
                return self.process_foreach(f)

            with cd(dirname):
                return self.process_foreach(f)

    def import_text(self, path, option=None):
        with open(path, 'r') as f:
            output = []
            for line in f:
                output.append(line.rstrip())

            return output

    def table_row(self, row):
        cells = []
        for cell in row:
            cell2 = cell
            cell2 = cell2.replace("\n", "<br>")
            cell2 = cell2.replace("|", "\x5d")
            cells.append(cell2)

        line = "| " + " | ".join(cells) + " |"
        return line

    def import_table(self, path, option=None):
        with open(path, encoding='utf8', newline='') as f:
            csvreader = csv.reader(f)
            output = []

            header = next(csvreader)
            output.append(self.table_row(header))

            line = "| "
            for i in range(0, len(header)):
                line = line + " :- |"
            output.append(line)

            for row in csvreader:
                output.append(self.table_row(row))

            return output
