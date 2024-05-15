#!/usr/bin/python3
'''
Script markdown2html.py converts Markdown files to HTML.
Takes 2 string arguments:
- Markdown file name
- Output file name
'''

import sys
import os.path
import re
import hashlib

def print_usage():
    print('Usage: ./markdown2html.py README.md README.html', file=sys.stderr)

def print_missing(filename):
    print('Missing {}'.format(filename), file=sys.stderr)

def convert_md5(content):
    return hashlib.md5(content.encode()).hexdigest()

def remove_c(content):
    return content.replace('C', '').replace('c', '')

def parse_headings(line):
    headings = line.lstrip('#')
    heading_num = len(line) - len(headings)
    return f'<h{heading_num}>{headings.strip()}</h{heading_num}>\n'

def parse_unordered(line):
    return f'<li>{line.lstrip("-").strip()}</li>\n'

def parse_ordered(line):
    return f'<li>{line.lstrip("*").strip()}</li>\n'

def parse_paragraph(line, in_paragraph):
    if not in_paragraph:
        return '<p>\n' + line + '\n', True
    else:
        return line + '\n', False

def parse_bold_and_emphasis(line):
    line = line.replace('**', '<b>', 1)
    line = line.replace('**', '</b>', 1)
    line = line.replace('__', '<em>', 1)
    line = line.replace('__', '</em>', 1)
    return line

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    md_file = sys.argv[1]
    html_file = sys.argv[2]

    if not os.path.isfile(md_file):
        print_missing(md_file)
        exit(1)

    with open(md_file) as markdown:
        with open(html_file, 'w') as html:
            unordered_list_start, ordered_list_start, paragraph = False, False, False
            for line in markdown:
                line = parse_bold_and_emphasis(line)

                md5_matches = re.findall(r'\[\[(.+?)\]\]', line)
                if md5_matches:
                    line = line.replace(f'[[{md5_matches[0]}]]', convert_md5(md5_matches[0]))

                remove_c_matches = re.findall(r'\(\((.+?)\)\)', line)
                if remove_c_matches:
                    line = line.replace(f'(({remove_c_matches[0]}))', remove_c(remove_c_matches[0]))

                if line.startswith('#'):
                    html.write(parse_headings(line))
                elif line.startswith('-'):
                    if not unordered_list_start:
                        html.write('<ul>\n')
                        unordered_list_start = True
                    html.write(parse_unordered(line))
                elif line.startswith('*'):
                    if not ordered_list_start:
                        html.write('<ol>\n')
                        ordered_list_start = True
                    html.write(parse_ordered(line))
                elif not line.strip():
                    if paragraph:
                        html.write('</p>\n')
                        paragraph = False
                else:
                    line, paragraph = parse_paragraph(line, paragraph)
                    html.write(line)

            if unordered_list_start:
                html.write('</ul>\n')
            if ordered_list_start:
                html.write('</ol>\n')
            if paragraph:
                html.write('</p>\n')
    exit(0)
