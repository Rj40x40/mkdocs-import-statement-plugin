# mkdocs-import-statement-plugin

This plugin is for [MkDocs](https://www.mkdocs.org/) to add capability of `@import "file"` statement to directly insert various files into a page.

## Supported file types

As image file type, following extensions are supported

| Extension | File type                          | Behavior |
| :-------- | :--------------------------------- | :------- |
| .jpeg     | JPEG                               | Image    |
| .jpg      | ^                                  | ^        |
| .gif      | Graphics Interchange Format        | ^        |
| .png      | Portable Network Graphics          | ^        |
| .apng     | Animated Portable Network Graphics | ^        |
| .svg      | Scalable Vector Graphics           | ^        |
| .bmp      | Windows bitmap                     | ^        |

Following extensions are also supported.

| Extension | File type              | Behavior   |
| :-------- | :--------------------- | :--------- |
| .csv      | Comma-Separated Values | Table      |
| .js       | JavaScript             | JavaScript |
| .md       | Markdown               | Markdown   |
| .html     | HTML                   | Text       |
| .htm      | ^                      | ^          |
| .mermaid  | Mermaid                | Comment    |
| .dot      | DOT                    | ^          |
| .puml     | PlantUML               | ^          |
| .pu       | ^                      | ^          |

## Installation

Install the plugin using `pip`:

```bash
pip install mkdocs-import-statement-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yml
plugins:
  - search
  - import-statement
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

## Usage

In your markdown documents you can describe as following.

```text
@import "file"
```

When you use MkDocs, this plugin will replace these import statements appropriately depending on the extension.

### Image file

The import statement is replaced as following.

```markdown
![](file)
```

If there are `{}` options after the import statement, that statement will be replaced with a `<img>` tag.

For example,

```text
@import "file" {width="640" height="480"}
```

is converted to as follwoing.

```html
<img src="file" width="640" height="480">
```

Where the image file path is relative to the markdown file.

### Table file

The import statement is replaced with a Markdown table that expands the contents of the specified file.

For example, when the following CSV file is as following.

```csv
A1,B1,C1
A2,B2,C2
A3,B3,C3
```

This replaced to as following.

```markdown
| A1 | B1 | C1 |
| :- | :- | :- |
| A2 | B2 | C2 |
| A3 | B3 | C3 |
```

### JavaScript file

The import statement is replaced with `<script>` tag like as following.

```html
<script type="text/javascript" src="file"></script>
```

### Markdown file

The import statement is replaced with the contents of the specified file and the replacement is recursively processed.

### Text file

The import statement is replaced with the contents of the specified file.

### Comment file

The import statement is replaced by comment blocks of the contents of the specified file.
