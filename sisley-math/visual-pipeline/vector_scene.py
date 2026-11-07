"""Preserve PDF drawing instructions as an editable, data-only SVG scene.

Drawing geometry and extracted labels are not inferred mathematical constraints.
"""
import json
import math
import re
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XLINK)
TAGS = {'svg','defs','g','path','rect','circle','ellipse','line','polyline','polygon',
        'clipPath','mask','use','symbol','linearGradient','radialGradient','stop',
        'title','desc','text','tspan'}


def encode(element):
    result = {'tag': element.tag.rsplit('}', 1)[-1], 'attributes': dict(element.attrib)}
    if element.text and element.text.strip():
        result['text'] = element.text
    if len(element):
        result['children'] = [encode(child) for child in element]
    return result


def validate(scene):
    if scene.get('version') != 1 or scene.get('kind') != 'vector':
        raise ValueError('Expected a version 1 vector scene')
    box = scene.get('view_box', [])
    if len(box) != 4 or not all(isinstance(v, (int,float)) and math.isfinite(v) for v in box) or min(box[2:]) <= 0:
        raise ValueError('Invalid vector scene view box')
    ids = set()
    references = []
    def walk(node):
        if node['tag'] not in TAGS:
            raise ValueError(f'Unsupported SVG element: {node["tag"]}')
        for key,value in node.get('attributes', {}).items():
            plain = key.rsplit('}',1)[-1]
            if plain.lower().startswith('on') or 'javascript:' in value.lower() or 'data:' in value.lower():
                raise ValueError('Executable or raster content is not a vector scene')
            if plain == 'href':
                if not value.startswith('#'):
                    raise ValueError('Only internal SVG references are permitted')
                references.append(value[1:])
            for reference in re.findall(r'url\(([^)]+)\)', value):
                if not reference.startswith('#'):
                    raise ValueError('External SVG resources are not permitted')
                references.append(reference[1:])
            if plain == 'id':
                if value in ids:
                    raise ValueError('Duplicate SVG element ID')
                ids.add(value)
        for child in node.get('children', []):
            walk(child)
    for element in scene['elements']:
        walk(element)
    if set(references) - ids:
        raise ValueError('Unresolved SVG reference')
    for matrix in scene.get('semantics', {}).get('matrices', []):
        rows = matrix['entries']
        if not rows or not rows[0] or len({len(row) for row in rows}) != 1:
            raise ValueError('Matrix rows must have consistent dimensions')
        if any(value is not None and not isinstance(value, (str,int,float)) for row in rows for value in row):
            raise ValueError('Matrix entries must be scalar values or explicit blank nulls')


def render(scene):
    validate(scene)
    box = scene['view_box']
    root = ET.Element(f'{{{SVG}}}svg', {'viewBox':' '.join(map(str,box)),
        'width':str(box[2]), 'height':str(box[3]), 'role':'img'})
    ET.SubElement(root, f'{{{SVG}}}title').text = scene['title']
    ET.SubElement(root, f'{{{SVG}}}desc').text = scene.get('description', 'Recovered drawing; original retained for comparison.')
    ET.SubElement(root, f'{{{SVG}}}rect', {'x':str(box[0]),'y':str(box[1]),
        'width':str(box[2]),'height':str(box[3]),'fill':'white'})
    def decode(node):
        element = ET.Element(f'{{{SVG}}}{node["tag"]}', node.get('attributes', {}))
        element.text = node.get('text')
        for child in node.get('children', []):
            element.append(decode(child))
        return element
    for node in scene['elements']:
        root.append(decode(node))
    return ET.tostring(root, encoding='unicode') + '\n'


def matrix_latex(entries):
    def entry(value):
        if value is None:
            return r'\phantom{0}'
        if isinstance(value, (int,float)) and value < 0:
            return '{}^{-}' + str(-value)
        return str(value)
    return r'\begin{bmatrix}' + r' \\ '.join(' & '.join(entry(v) for v in row) for row in entries) + r'\end{bmatrix}'


def latex_records(scene):
    semantics = scene.get('semantics', {})
    return ([{'id':m['id'],'latex':matrix_latex(m['entries'])} for m in semantics.get('matrices', [])]
            + [{'id':f['id'],'latex':f['latex']} for f in semantics.get('expressions', [])])
