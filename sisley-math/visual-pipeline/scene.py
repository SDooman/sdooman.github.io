"""A small, data-only directed multigraph renderer. Layout is not mathematical data."""
import html
import math


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(scene):
    if scene.get('version') != 1 or scene.get('kind') != 'network':
        raise ValueError('Only version 1 network scenes are implemented')
    for key in ('width', 'height'):
        if not finite(scene.get(key)) or scene[key] <= 0:
            raise ValueError(f'Invalid scene {key}')
    nodes = scene.get('nodes', [])
    ids = [n['id'] for n in nodes]
    if not nodes or len(ids) != len(set(ids)):
        raise ValueError('Node IDs must be unique and nonempty')
    for node in nodes:
        if not isinstance(node['id'], str) or not isinstance(node.get('label'), str):
            raise ValueError('Node IDs and labels must be strings')
        if any(not finite(node.get(k)) for k in ('x', 'y', 'label_dx', 'label_dy')):
            raise ValueError('Node layout coordinates must be finite')
    edge_ids = set()
    for edge in scene.get('edges', []):
        if edge['id'] in edge_ids or edge['from'] not in ids or edge['to'] not in ids:
            raise ValueError('Duplicate edge ID or missing endpoint')
        edge_ids.add(edge['id'])
        if edge.get('directed') is not True:
            raise ValueError('This renderer currently requires directed edges')
        if not finite(edge.get('arrow_at', .55)) or not .02 <= edge.get('arrow_at', .55) <= .98:
            raise ValueError('Arrow position must be between .02 and .98')
        controls = edge.get('controls', [])
        if len(controls) not in (0, 1, 2) or any(len(p) != 2 or not all(map(finite, p)) for p in controls):
            raise ValueError('Use zero, one (quadratic) or two (cubic) control points')
        if edge['from'] == edge['to'] and len(controls) != 2:
            raise ValueError('Loops need two cubic control points')


def render(scene):
    validate(scene)
    esc = lambda s: html.escape(str(s), quote=True)
    nodes = {n['id']: n for n in scene['nodes']}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {scene["width"]} {scene["height"]}" role="img">',
             f'<title>{esc(scene.get("title", "Directed network"))}</title>',
             '<rect width="100%" height="100%" fill="white"/>']
    for edge in scene['edges']:
        a, b = nodes[edge['from']], nodes[edge['to']]
        points = [[a['x'], a['y']], *edge.get('controls', []), [b['x'], b['y']]]
        command = {2: 'L', 3: 'Q', 4: 'C'}[len(points)]
        d = f'M {points[0][0]} {points[0][1]} {command} ' + ' '.join(f'{p[0]} {p[1]}' for p in points[1:])
        # A midpoint arrow avoids losing direction under a filled endpoint node.
        def bezier(t):
            work = [p[:] for p in points]
            while len(work) > 1:
                work = [[(1-t)*u[k]+t*v[k] for k in (0,1)] for u,v in zip(work,work[1:])]
            return work[0]
        t = edge.get('arrow_at', .55)
        centre = bezier(t)
        before, after = bezier(t-.01), bezier(t+.01)
        angle = math.degrees(math.atan2(after[1]-before[1], after[0]-before[0]))
        parts.append(f'<g data-edge="{esc(edge["id"])}"><title>{esc(edge["from"])} to {esc(edge["to"])}</title><path d="{d}" fill="none" stroke="black" stroke-width="3"/><path d="M 12 0 L -10 -9 L -10 9 Z" transform="translate({centre[0]} {centre[1]}) rotate({angle})"/></g>')
    for node in nodes.values():
        parts.append(f'<g data-node="{esc(node["id"])}"><circle cx="{node["x"]}" cy="{node["y"]}" r="9"/><text x="{node["x"]+node["label_dx"]}" y="{node["y"]+node["label_dy"]}" font-family="serif" font-size="28">{esc(node["label"])}</text></g>')
    return '\n'.join(parts + ['</svg>']) + '\n'


def adjacency(scene):
    validate(scene)
    ids = [n['id'] for n in scene['nodes']]
    index = {node: i for i, node in enumerate(ids)}
    rows = [[0] * len(ids) for _ in ids]
    for edge in scene['edges']:
        rows[index[edge['from']]][index[edge['to']]] += 1
    return {'node_order': ids, 'convention': 'row = from, column = to; entries count directed edges', 'matrix': rows}
