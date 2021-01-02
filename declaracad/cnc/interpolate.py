"""
Copyright (c) 2020, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Dec 27, 2020

@author: jrm
"""
from declaracad.occ.api import Topology, Wire


def distance(points, start, end, scale=-1):
    """ Set the z-value of the points by interpolating the
    distance from start and end points. If the first two points are equal
    None is returned.

    Parameters
    ----------
    points: List[Point]
        List of 2d points interpolate
    start: Float
        The starting z-value
    end: Float
        The ending z-value
    scale: Float
        Scale to apply to interpolation

    Returns
    -------
    points: List[Point] or None
        The list of interpolated points on the curve

    """
    p0, p1 = points[0:2]
    if p0 == p1:
        None  # Line is vertical

    p0.z = start * scale
    p1.z = end * scale
    dz = (end - start) * scale

    if len(points) != 2:
        # Determine z value
        z = p0.z
        dt = 0  # Distance
        last = points[0]

        # Determine total distance
        for p in points[1:]:
            dt += last.distance2d(p)
            last = p

        # Determine distance at each point to calculate t
        d = 0
        last = points[0]
        for p in points[1:]:
            d += last.distance2d(p)
            t = d/dt
            assert 0 <= t <= 1
            p.z = (z + dz*t)
            last = p
    return points


def lookup_vertex(graph, v):
    """ Lookup the vertex in the graph using the hash, if that fails,
    fallback to using equals to find points that are equal within
    the tolerance.

    Parameters
    ----------
    graph: Dict
        Mapping of Point to items
    v: Point
        The point to find

    Return
    ------
    entry: Tuple or None
        If the vertex is found return vertex and matching item in the graph.
    """
    item = graph.get(v)
    if item is not None:
        return (v, item)
    for vertex, item in graph.items():
        if vertex == v:
            return (vertex, item)


def build_edge_graph(shapes):
    """ Build a graph of verticies and edges that connect them. This assumes
    that all edges are unique.

    Parameters
    ----------
    shapes: Iterable[TopoDS_Shape]
        Iterable of shapes to build an edge graph from

    Returns
    -------
    graph: Dict
        A mapping of points to the list of connected edge topologies

    """
    graph = {}
    for s in shapes:
        for e in Topology(shape=s).edges:
            edge_topo = Topology(shape=e)
            for p in edge_topo.points:
                r = graph.get(p)
                if r is None:
                    # Lookup using equals instead of hash
                    for node in graph:
                        if node == p:
                            r = graph[node]
                            break
                    if r is None:
                        r = graph[p] = []
                r.append(edge_topo)
    return graph


def walk_edges(graph, vertex, edge):
    """ Start at the given vertex and walk the edge until a leaf or branch
    is found.

    Parameters
    ----------
    graph: Dict
        The graph to walk.
    vertex: Point
        The point to start at
    edge: TopoDS_Edge
        The edge to walk.

    Yields
    ------
    result: Tuple[Point, TopoDS_Edge or None]
        The vertex and edge walked. When the terminating vertex is found
        the edge is None.

    """
    used = set() # TODO: Detect loops
    vertex, topos = lookup_vertex(graph, vertex)
    topo = None
    for t in topos:
        if t.shape == edge:
            topo = t
            yield (vertex, edge)
            break
    if topo is None:
        raise ValueError("Edge is not connected")
    while True:
        # Find other point
        other_vertices = [p for p in topo.points if p != vertex]
        assert len(other_vertices) == 1
        next_vertex = other_vertices[0]
        assert vertex != next_vertex
        vertex, topos = lookup_vertex(graph, next_vertex)
        if len(topos) != 2:
            yield (vertex, None) # Final vertex, done
            break

        # Find other edge
        other_edges = [t for t in topos if not t.shape.IsSame(edge)]
        assert len(other_edges) == 1
        topo = other_edges[0]
        edge = topo.shape
        yield (vertex, edge)


def split_wires(graph):
    """ Split the graph into wires at their branch points.

    Parameters
    ----------
    wire: List[TopoDS_Wire]
        The list is wires to split
    graph:

    Yields
    ------
    wire: TopoDS_Wire
        Each wire in the graph

    """
    visited_edges = []
    for vertex, topos in graph.items():
        if len(topos) == 2:
            continue
        for topo in topos:
            edge = topo.shape
            if Topology.is_shape_in_list(edge, visited_edges):
                continue
            edges = [e for v, e in walk_edges(graph, vertex, edge)
                     if e is not None]
            yield Wire(edges=edges).render()

            # Add first and last edges to visited list
            visited_edges.append(edges[0])
            if len(edges) > 1:
                visited_edges.append(edges[-1])


def group_connected_wires(wires):
    """ Put the list of wires into a group if they are connected in the same
    graph.

    Parameters
    ----------
    wires: List[TopoDS_Wire]

    Returns
    -------
    groups: List[Dict]
        List of groups of connected wires.

    """
    groups = []
    for w in wires:
        topo = Topology(shape=w)
        group = None
        for g in groups:
            if any(topo.intersection(w) for w in g):
                group = g
                group.append(w)
                break
        if group is None:
            groups.append([w])
    return groups
