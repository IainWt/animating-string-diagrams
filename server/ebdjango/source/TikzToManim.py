from dataclasses import dataclass
from typing import Dict, List, Tuple
from .TikzParser import TikzLine, TikzNode, TikzParser, Location
from manim.utils.color.core import ManimColor
import math
from shapely.geometry import LineString
from manim import *
from .Nodes import create_and_position_node

"""
TikzToManim should convert a TikZ wrapper instance into an instance with values for Manim use

TikZ wrapper:
- nodes: style, id, position, label
- lines: start_id, end_id, in_angle, out_angle, looseness
- styles: name, props

### OUTPUT ###

Manim Diagram data structure
Nodes:
- id - can be stored in dictionary as keys for corresponding nodes
- position - converted to Manim coordinates
- label - can remain the same
- props - style properties converted to Manim properties

Lines:
- start_id - remain the same
- end_id - remain the same
- curve points - Manim coordinates of Bezier handle points


"""


@dataclass
class ManimInputNode():
  id: str
  position: List[float]
  label: str
  props: Dict[str, str]


@dataclass
class ManimInputLine():
  start_id: str
  end_id: str
  curve_points: List[List[float]]


@dataclass
class ManimInputDiagram():
  nodes: List[ManimInputNode]
  lines: List[ManimInputLine]


class TikzToManimConverter():

  def __init__(self, tikz_diagram, manim_x_limits, manim_y_limits) -> None:
    self.x_min, self.x_max, self.y_min, self.y_max = self.calculate_tikz_limits(tikz_diagram)
    self.MANIM_X_LIMITS, self.MANIM_Y_LIMITS, self.scale_factor = self.find_manim_limits(manim_x_limits, manim_y_limits)
    self.styles = tikz_diagram.styles
    self.node_positions: Dict[str, List[float]] = {}
    self.nodes = self.convert_nodes(tikz_diagram.nodes)
    self.nodes_by_id = self.create_node_dict(self.nodes)
    self.lines = self.convert_lines(tikz_diagram.lines)
    print("------ STYLES -----")
    print(tikz_diagram.styles)
    print(self.styles)
    print("------ NODES ------")
    print(tikz_diagram.nodes)
    print(self.nodes)
    print("------ LINES ------")
    print(tikz_diagram.lines)
    print(self.lines)

  
  def calculate_tikz_limits(self, tikz_diagram):
    """Takes a TikzDiagram and returns the min & max x & y coordinates"""
    x_coords = [node.position[0] for node in tikz_diagram.nodes]
    y_coords = [node.position[1] for node in tikz_diagram.nodes]
    return min(x_coords), max(x_coords), min(y_coords), max(y_coords)
  

  def scale_limits(self, scale_factor, tikz_limits, manim_limits):
      # find midpoint of ranges
      tikz_midpoint = sum(tikz_limits) / 2
      manim_midpoint = sum(manim_limits) / 2
      # scale limits on smaller range & add manim range midpoint
      new_limits = [((limit - tikz_midpoint) * scale_factor) + manim_midpoint for limit in tikz_limits]
      return new_limits


  def find_manim_limits(self, manim_x_limits, manim_y_limits):
    # find largest tikz axis related to manim axis - x range / manim x range & y range / manim y range
    print(manim_y_limits, [self.y_min, self.y_max])
    x_scale_factor = (manim_x_limits[1] - manim_x_limits[0]) / (self.x_max - self.x_min) if self.x_max - self.x_min != 0 else 0
    y_scale_factor = (manim_y_limits[1] - manim_y_limits[0]) / (self.y_max - self.y_min) if self.y_max - self.y_min != 0 else 0
    # take smallest as manim limits - scale other axis limits down (because small tikz range has large scale factor)
    if y_scale_factor >= x_scale_factor:
      new_x_limits = manim_x_limits
      new_y_limits = self.scale_limits(x_scale_factor, [self.y_min, self.y_max], manim_y_limits)
      new_scale_factor = x_scale_factor
    else:
      new_y_limits = manim_y_limits
      new_x_limits = self.scale_limits(y_scale_factor, [self.x_min, self.x_max], manim_x_limits)
      new_scale_factor = y_scale_factor

    return new_x_limits, new_y_limits, new_scale_factor


  def manim_coord_from_tikz_coord(self, tikz_position: Tuple[float]) -> List[float]:
    """Calculate Manim equivalent of TikZ coordinate"""
    # x_frax & y_frac are distance along axis as fraction of axis length
    if self.x_max - self.x_min == 0:
      x_frac = 0
    else:
      x_frac = (tikz_position[0] - self.x_min) / (self.x_max - self.x_min)
    # scale fraction to manim axis length and move so axis covers 0
    manim_x = x_frac * (self.MANIM_X_LIMITS[1] - self.MANIM_X_LIMITS[0]) + self.MANIM_X_LIMITS[0]

    if self.y_max - self.y_min == 0:
      y_frac = 0
    else:
      y_frac = (tikz_position[1] - self.y_min) / (self.y_max - self.y_min)
    manim_y = y_frac * (self.MANIM_Y_LIMITS[1] - self.MANIM_Y_LIMITS[0]) + self.MANIM_Y_LIMITS[0]
    return [manim_x, manim_y, 0]
  

  ######################### NODES ######################

  def convert_prop_name(self, prop: str):
    """Convert a TikZ property name to the corresponding Manim property
    
    Currently converts TikZ properties fill, draw, minimum width, minimum height
    to Manim fill_color, stroke_color, width, height"""
    if prop == 'fill': return 'fill_color'
    if prop == 'draw': return 'stroke_color'
    if prop == 'shape': return 'shape'
    if prop == 'minimum width' or prop == 'width': return 'width'
    if prop == 'minimum height' or prop == 'height': return 'height'
    return prop


  def convert_color(self, color: str):
    """Convert a TikZ color name into a Manim color value
    
    Currently only deals with colors where name is the same in Manim"""
    try:
      manim_color = ManimColor.parse(color)
      return manim_color
    except:
      raise Exception("Unable to convert TikZ color:", color)
    

  def convert_size(self, size: float):
    new_size = size * self.scale_factor
    return new_size


  def convert_properties(self, props: Dict[str,str]) -> Dict[str,str]:
    """Convert a dictionary of TikZ properties & values to Manim ones"""
    manim_props = {}
    for prop, value in props.items():
      manim_prop = self.convert_prop_name(prop)
      if manim_prop:
        # Convert colors
        if 'color' in manim_prop:
          manim_value = self.convert_color(value)
        # Convert measurement in cm

        else:
          # Convert value to float if possible
          try:
            manim_value = float(value)
            if manim_prop == 'width' or manim_prop == 'height':
              manim_value = self.convert_size(manim_value)
          # Other strings
          except ValueError:
            manim_value = value
        manim_props[manim_prop] = manim_value
    if manim_props == {}:
      manim_props['shape'] = 'none'
    return manim_props


  def input_node_from_tikz_node(self, tikz_node: TikzNode) -> ManimInputNode:
    """Convert all properties of a TikzNode"""
    id = tikz_node.id
    position = self.manim_coord_from_tikz_coord(tikz_node.position)
    self.node_positions[id] = position
    label = tikz_node.label
    props = self.styles[tikz_node.style] if tikz_node.style != 'none' else {}
    manim_props = self.convert_properties(props)
    return ManimInputNode(id, position, label, manim_props)
  

  def convert_nodes(self, nodes: List[TikzNode]) -> List[ManimInputNode]:
    return [self.input_node_from_tikz_node(node) for node in nodes]
  

  def create_node_dict(self, nodes: List[ManimInputNode]):
    return {node.id: node for node in nodes}
  
  
  ##################### LINES ##########################

  def point_using_dist_and_angle(self, point1: List[float], dist: float, angle: float) -> List[float]:
    """Calculate coordinates of second point using distance and angle from first point"""
    x1, y1, _ = point1
    angle_radians = math.radians(angle)
    x2 = x1 + dist * math.cos(angle_radians)
    y2 = y1 + dist * math.sin(angle_radians)
    return [x2, y2, 0]
  

  def manim_dir_from_compass_dir_part(self, compass_dir: str):
    compass_dir = compass_dir.lower()
    if compass_dir == 'north': return UP
    if compass_dir == 'east': return RIGHT
    if compass_dir == 'south': return DOWN
    if compass_dir == 'west': return LEFT
  

  def manim_dir_from_full_compass_dir(self, dir: str):
    dir_parts = dir.split(' ')
    manim_dirs = [self.manim_dir_from_compass_dir_part(dir_part) for dir_part in dir_parts]
    return sum(manim_dirs)
  

  def edge_point_from_compass_dir(self, node_id: str, dir: str): 
    node = self.nodes_by_id[node_id]

    manim_node = create_and_position_node(node)

    size = max(manim_node.width, manim_node.height)
    manim_dir = self.manim_dir_from_full_compass_dir(dir)
    line = [manim_node.get_center(), manim_node.get_center() + (manim_dir * size)]

    edge_points = list(manim_node.shape.points)
    edge_points.append(manim_node.shape.points[0])

    for i in range(len(edge_points) - 1):
      shape_edge_line = [edge_points[i], edge_points[i+1]]
      line1 = LineString(line)
      line2 = LineString(shape_edge_line)

      if line1.intersects(line2):
        intersection_point = line1.intersection(line2)
        intersection_coords = [intersection_point.x, intersection_point.y, 0]
        return intersection_coords
      
  
  def calculate_angle_between_points(self, point1: List[float], point2: List[float]):
    y = point2[1] - point1[1]
    x = point2[0] - point1[0]
    angle_rad = math.atan2(y, x)
    angle_deg = math.degrees(angle_rad)
    return angle_deg
  

  def calculate_handle_points(self, start_point: List[float], end_point: List[float], line: TikzLine) -> List[List[float]]:
    """Calculate all handle points for TikZ line to be represented as a bezier curve"""

    if not line.looseness: line.looseness = 1
    if line.in_angle == None or line.out_angle == None:
      line.out_angle = self.calculate_angle_between_points(start_point, end_point)
      line.in_angle = self.calculate_angle_between_points(end_point, start_point)

    SCALING_CONST = 0.4
    dist_between_points = math.dist(start_point, end_point)
    # Looseness of 1 means handle points are 2/5 of between-endpoint distance away from endpoint
    handle_dist_from_ends = dist_between_points * SCALING_CONST * line.looseness
    handle_point1 = self.point_using_dist_and_angle(start_point, handle_dist_from_ends, line.out_angle)
    handle_point2 = self.point_using_dist_and_angle(end_point, handle_dist_from_ends, line.in_angle)
    return [start_point, handle_point1, handle_point2, end_point]
  

  def manim_coord_from_tikz_location(self, loc: Location):
    if loc.type == 'id':
      return self.node_positions[loc.location]
    if loc.type == 'coordinate':
      return self.manim_coord_from_tikz_coord(loc.location)
    if loc.type == 'compass':
      return self.edge_point_from_compass_dir(loc.location['id'], loc.location['direction'])
    

  def get_id_from_tikz_location(self, loc: Location):
    if loc.type == 'id':
      return loc.location
    if loc.type == 'coordinate':
      return self.manim_coord_from_tikz_coord(loc.location)
    if loc.type == 'compass':
      return f"{loc.location['id']}.{loc.location['direction']}"
  

  def input_line_from_tikz_line(self, tikz_line: TikzLine) -> ManimInputLine:
    start_loc = tikz_line.start_loc
    end_loc = tikz_line.end_loc
    # get position of points after conversion
    start_point = self.get_id_from_tikz_location(start_loc)
    end_point = self.get_id_from_tikz_location(end_loc)
    start_coord = self.manim_coord_from_tikz_location(start_loc)
    end_coord = self.manim_coord_from_tikz_location(end_loc)
    curve_points = self.calculate_handle_points(start_coord, end_coord, tikz_line)
    return ManimInputLine(str(start_point), str(end_point), curve_points)
  

  def convert_lines(self, lines: List[TikzLine]) -> List[ManimInputLine]:
    return [self.input_line_from_tikz_line(line) for line in lines]





### FOR TESTING ###

test_styles = r"""
% \tikzstyle{NAME}=[PROPERTY LIST]
\tikzstyle{red dot}=[fill=red, draw=black, shape=circle]"""


test_tikz = r"""\begin{pgfonlayer}{nodelayer}
		\node [style=red dot] (0) at (-7.25, 0) {$a$};
		\node [style=none] (10) at (-3.75, -1) {};
    \node[style=none] (m0) at (-7.25, 0) {m0};
	\end{pgfonlayer}
	\begin{pgfonlayer}{edgelayer}
		\draw [in=-180, out=0, looseness=0.75] (0) to (10);
    \draw [bend right=90, looseness=1.25] (0) to (10);
    \draw (m0.south east) to[out=-60, in=90] (8.25, 2);
	\end{pgfonlayer}"""

if __name__ == '__main__':
  tikz_diagram = TikzParser.parse_tikz_diagram(test_tikz, test_styles)
  tikz_to_manim_converter = TikzToManimConverter(tikz_diagram, [6,6], [3,3])
  print(tikz_to_manim_converter.nodes)
  print(tikz_to_manim_converter.point_using_dist_and_angle([0,0,0], math.sqrt(2), -135))
  print(tikz_to_manim_converter.lines)




