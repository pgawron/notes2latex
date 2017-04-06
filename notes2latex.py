#!/usr/bin/env python
import poppler
import sys
import urllib
import os
import subprocess
import shlex
import pprint

SYNCTEX_BIN = '/usr/bin/synctex'


def get_latex_position(page_no, page_size, rect, synctex_pdf):
    x = rect.x1 + (rect.x2 - rect.x1) / 2
    y = rect.y1 + (rect.y2 - rect.y1) / 2
    command = SYNCTEX_BIN + ' edit -o %d:%d:%d:%s' % (page_no, x, page_size[1] - y, synctex_pdf)
    args = shlex.split(command)
    lines = subprocess.check_output(args=args).split('\n')
    data = {}
    for line in lines:
        p = line.split(":")
        if len(p) == 2:
            data[p[0]] = p[1]
    return data


def get_annotations(annotated_pdf, synctex_pdf):
    document = poppler.document_new_from_file('file://%s' % \
                                              urllib.pathname2url(os.path.abspath(annotated_pdf)), None)
    n_pages = document.get_n_pages()
    all_annots = 0

    annotation_data = []
    input_filenames = set()
    for page_no in range(n_pages):
        page = document.get_page(page_no)
        annot_mappings = page.get_annot_mapping()
        num_annots = len(annot_mappings)
        if num_annots > 0:
            for annot_mapping in annot_mappings:
                if annot_mapping.annot.get_annot_type().value_name != 'POPPLER_ANNOT_LINK':
                    all_annots += 1
                    rect = annot_mapping.area
                    data = get_latex_position(page_no + 1, page.get_size(), rect, synctex_pdf)
                    data["AnnotType"] = annot_mapping.annot.get_annot_type().value_nick
                    data["Page"] = str(page_no + 1)
                    data["Modified"] = annot_mapping.annot.get_modified()
                    data["Contents"] = annot_mapping.annot.get_contents()
                    annotation_data.append(data)
                    input_filenames.add(data['Input'])
    return annotation_data, input_filenames


def main():
    if len(sys.argv) != 3:
        print("python notes2latex.py annotated.pdf synctexed.pdf ")
        exit(1)
    else:
        annotated_pdf = sys.argv[1]
        synctex_pdf = sys.argv[2]

        annotation_data, input_filenames = get_annotations(annotated_pdf, synctex_pdf)

        latex_lines_dict = {}
        for input_filename in input_filenames:
            with open(input_filename, 'r') as fin:
                latex_lines_dict[input_filename] = fin.readlines()

        for annotation in annotation_data:
            pprint.pprint(annotation)
            line_no = int(annotation["Line"]) - 1
            input_filename = annotation['Input']
            if annotation["Contents"]:
                annotation_text = "%<ann> "
                annotation_text += ' '.join(annotation["Contents"].splitlines())
                annotation_text += " </ann>\n"
                print(input_filename)
                print(annotation_text)
                latex_lines_dict[input_filename][line_no] += annotation_text

        for input_filename in input_filenames:
            with open(input_filename, 'w') as fout:
                for line in latex_lines_dict[input_filename]:
                    fout.write(line)

        exit(0)


if __name__ == "__main__":
    main()
