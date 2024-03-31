import math
from typing import Dict, List, Sequence, Tuple
from manim import *
from manim.camera.camera import Camera

from .TikzParser import TikzParser
from .TikzToManim import ManimInputLine, ManimInputNode, TikzToManimConverter
from .Nodes import create_shape, Node


MANIM_X_LIMIT = 6
MANIM_Y_LIMIT = 3


class Diagram(VGroup):
  def __init__(self, tikz_to_manim_converter: TikzToManimConverter, diagram_info, **kwargs):
    super().__init__(**kwargs)
    self.LINE_LAYER = 0
    self.NODE_LAYER = 1
    self.node_ids: Dict[str, Node] = {}
    self.line_ids: Dict[Tuple[str, str], CubicBezier] = {}
    self.subtitle = None
    self.create_lines(tikz_to_manim_converter.lines)
    self.create_nodes(tikz_to_manim_converter.nodes)
    self.create_subtitle(diagram_info['subtitle'])


  def create_nodes(self, nodes: List[ManimInputNode]):
    for node in nodes:
      shape = create_shape(node.label, **node.props)
      shape.move_to(node.position)
      shape.set_z_index(self.NODE_LAYER)
      self.node_ids[node.id] = shape
      self.add(shape)


  def create_lines(self, lines: List[ManimInputLine]):
    for line in lines:
      bezier = CubicBezier(*line.curve_points, color=BLACK)
      bezier.set_z_index(self.LINE_LAYER)
      self.line_ids[(line.start_id, line.end_id)] = bezier
      self.add(bezier)


  def create_subtitle(self, subtitle_text):
    if len(subtitle_text) > 0:
      subtitle = Text(subtitle_text, color=BLACK)
      subtitle.move_to(DOWN * MANIM_Y_LIMIT)
      self.subtitle = subtitle
      self.add(subtitle)



class DiagramScene(Scene):
  def __init__(self, tikz_and_style_pairs, extra_info=[{}], **kwargs):
    super().__init__(**kwargs)
    self.tikz_and_style_pairs = tikz_and_style_pairs
    self.extra_info = extra_info


  def get_transitions_between_nodes(self, diagram1: Diagram, diagram2: Diagram):
    """Create transitions between nodes of two diagrams
    
    Any nodes in first but not second will fade out.
    Any nodes in second but not in first will fade in."""
    transitions = []
    for node1_id, node1 in diagram1.node_ids.items():
      node2 = diagram2.node_ids.get(node1_id, 0)
      # Nodes which are in both diagrams
      if node2 != 0:
        transitions.append(ReplacementTransform(node1, node2))
      # Nodes which are only in diagram 1
      else:
        transitions.append(FadeOut(node1))

    # Nodes which are only in diagram 2
    remaining_node_ids = set(diagram2.node_ids) - set(diagram1.node_ids)
    for node_id in remaining_node_ids:
      node = diagram2.node_ids[node_id]
      transitions.append(FadeIn(node))

    return transitions
  

  def find_line_with_shared_point(self, line_id, end_index, other_line_ids):
    """Find another line which shares an endpoint with the first line
    
    end_index of 0 looks for shared start point
    end_index of 1 looks for shared end point"""
    for other_line_id in other_line_ids:
      if other_line_id[end_index] == line_id[end_index]:
        return other_line_id
    return None
  

  def get_transitions_between_lines(self, diagram1: Diagram, diagram2: Diagram):
    transitions = []
    line_ids_to_remove = []
    for line1_id, line1 in diagram1.line_ids.items():
      line2 = diagram2.line_ids.get(line1_id, 0)
      # Lines which are in both diagrams
      if line2 != 0:
        transitions.append(ReplacementTransform(line1, line2))
      # Lines which are only in diagram 1
      else:
        line_ids_to_remove.append(line1_id)

    # Lines which are only in diagram 2
    line_ids_to_add = set(diagram2.line_ids) - set(diagram1.line_ids)

    # Look for lines with same start point to transition to - if none, those with same endpoint
    for endpoint_index in [0, 1]:
      for line_id_to_remove in line_ids_to_remove:
        line_id_to_add = self.find_line_with_shared_point(line_id_to_remove, endpoint_index, line_ids_to_add)
        if line_id_to_add:
          transitions.append(ReplacementTransform(diagram1.line_ids[line_id_to_remove], diagram2.line_ids[line_id_to_add]))
          line_ids_to_add.remove(line_id_to_add)
          line_ids_to_remove.remove(line_id_to_remove)
    
    transitions += [FadeOut(diagram1.line_ids[line_id]) for line_id in line_ids_to_remove]
    transitions += [Create(diagram2.line_ids[line_id]) for line_id in line_ids_to_add]

    return transitions
  
  
  def get_subtitle_transitions(self, diagram1: Diagram, diagram2: Diagram):
    """Get fade out & fade in transitions for subtitles between diagrams"""
    transitions = []
    if diagram1.subtitle: transitions.append(FadeOut(diagram1.subtitle))
    if diagram2.subtitle: transitions.append(FadeIn(diagram2.subtitle))
    return transitions


  def transition_between_all_diagrams(self, diagrams: List[Diagram]):
    self.add(diagrams[0])
    self.wait(1)

    for i in range(1, len(diagrams)):
      line_transitions = self.get_transitions_between_lines(diagrams[i-1], diagrams[i])
      node_transitions = self.get_transitions_between_nodes(diagrams[i-1], diagrams[i])
      subtitle_transitions = self.get_subtitle_transitions(diagrams[i-1], diagrams[i])
      all_transitions = [*line_transitions, *node_transitions, *subtitle_transitions]

      self.play(*all_transitions)
      self.wait(1)


  def construct(self):

    self.camera.background_color = WHITE

    diagrams = []
    manim_x_limits = [-MANIM_X_LIMIT, MANIM_X_LIMIT]
    manim_y_limits = [-MANIM_Y_LIMIT, MANIM_Y_LIMIT]

    # Make space at bottom if any subtitles in animation
    subtitles = [diagram_info['subtitle'] for diagram_info in self.extra_info.values() if len(diagram_info['subtitle']) > 0]
    if len(subtitles) > 0:
      manim_y_limits[0] += 1

    for id, tikz_and_style_pair in enumerate(self.tikz_and_style_pairs):
      test_tikz, test_styles = tikz_and_style_pair
      tikz_diagram = TikzParser.parse_tikz_diagram(test_tikz, test_styles)
      tikz_to_manim_converter = TikzToManimConverter(tikz_diagram, manim_x_limits, manim_y_limits)
      diagrams.append(Diagram(tikz_to_manim_converter, self.extra_info[id]))

    self.transition_between_all_diagrams(diagrams)









### FOR TESTING ###
  


test_styles = r"""% TiKZ style file generated by TikZiT. You may edit this file manually,
  % but some things (e.g. comments) may be overwritten. To be readable in
  % TikZiT, the only non-comment lines must be of the form:
  % \tikzstyle{NAME}=[PROPERTY LIST]

  % Node styles
  \tikzstyle{red dot}=[fill=red, draw=black, shape=circle]
  \tikzstyle{green dot}=[fill=green, draw=black, shape=circle]
  \tikzstyle{white square}=[fill=white, draw=black, shape=rectangle]

  % Edge styles"""


test_tikz = r"""\begin{pgfonlayer}{nodelayer}
    \node [style=white square] (0) at (-7.25, 0) {$a$};
    \node [style=green dot] (1) at (-5.75, 0) {$b$};
    \node [style=white square] (2) at (-4.25, 1) {$2$};
    \node [style=white square] (3) at (-2.75, 1) {$3$};
    \node [style=white square] (4) at (-5.75, -1) {$4$};
    \node [style=none] (5) at (-7.5, 1) {};
    \node [style=none] (6) at (-7.5, -1) {};
    \node [style=none] (7) at (-2.25, 0) {};
    \node [style=none] (8) at (-2.25, -1) {};
    \node [style=none] (9) at (-3.75, 0) {};
    \node [style=none] (10) at (-3.75, -1) {};
  \end{pgfonlayer}
  \begin{pgfonlayer}{edgelayer}
    \draw (0) to (1);
    \draw [in=-180, out=0, looseness=0.75] (5.center) to (2);
    \draw [in=-165, out=15, looseness=1.25] (1) to (2);
    \draw (6.center) to (4);
    \draw (2) to (3);
    \draw [in=180, out=0] (1) to (10.center);
    \draw [in=180, out=0] (4) to (9.center);
    \draw (9.center) to (7.center);
    \draw (10.center) to (8.center);
    \draw [bend left=135, looseness=1.5] (0) to (1);
  \end{pgfonlayer}"""

test_tikz2 = r"""\begin{pgfonlayer}{nodelayer}
    \node [style=white square] (0) at (-7.25, 0) {$a$};
    \node [style=green dot] (1) at (-5.75, 0) {$b$};
    \node [style=white square] (2) at (-2.75, -1) {$2$};
    \node [style=white square] (3) at (-2.75, 1) {$3$};
    \node [style=white square] (4) at (-5.75, -1) {$4$};
    \node [style=none] (5) at (-7.5, 1) {};
    \node [style=none] (6) at (-7.5, -1) {};
    \node [style=none] (7) at (-2.25, 0) {};
    \node [style=none] (8) at (-2.25, -1) {};
    \node [style=none] (9) at (-3.75, 0) {};
    \node [style=none] (10) at (-3.75, -1) {};
  \end{pgfonlayer}
  \begin{pgfonlayer}{edgelayer}
    \draw (0) to (1);
    \draw [in=-180, out=0, looseness=0.75] (5.center) to (2);
    \draw [in=-165, out=15, looseness=1.25] (1) to (2);
    \draw (6.center) to (4);
    \draw (2) to (3);
    \draw [in=180, out=0] (1) to (10.center);
    \draw [in=180, out=0] (4) to (3);
    \draw (9.center) to (7.center);
    \draw (10.center) to (8.center);
    \draw [bend left=135, looseness=1.5] (0) to (1);
  \end{pgfonlayer}"""









########################### CURRENTLY UNUSED ##############################




def string_to_direction(string: str):
  if string == 'left': return LEFT
  elif string == 'right': return RIGHT
  elif string == 'up': return UP
  elif string == 'down': return DOWN
  else:
    raise Exception("Direction string must be left, right, up, or down")
  

def get_square_edge_center(square, side):
  center = square.get_center()
  if side == 'left':
    return center + LEFT * square.width / 2
  elif side == 'right':
    return center + RIGHT * square.width / 2
  elif side == 'top':
    return center + UP * square.width / 2
  elif side == 'bottom':
    return center + DOWN * square.width / 2


def connect_with_line(square1: Node, side1: str, square2: Node, side2: str, lines):
  square1.add_line(side1)
  square2.add_line(side2)
  lines.append(((square1, side1), (square2, side2)))

  
def create_bezier(end_point1, end_point2):
  p1 = end_point1 + RIGHT
  p2 = end_point2 + LEFT

  # Show control points for testing (need to pass self)
  # bezier_points = [end_point1, p1, p2, end_point2]
  # for point in bezier_points:
  #   self.add(Dot(point))

  return CubicBezier(end_point1, p1, p2, end_point2)


def position_lines(lines):
  beziers = []
  for line in lines:
    square1 = line[0][0]
    point1 = square1.get_line_endpoint(line[0][1])
    square2 = line[1][0]
    point2 = square2.get_line_endpoint(line[1][1])
    beziers.append(create_bezier(point1, point2))

  return beziers




  # Add one to number of lines on a side (CURRENTLY UNUSED)
  # def add_line(self, side: str):
  #   self.line_nums[side] = self.line_nums.get(side, 0) + 1
  #   self.available_line_nums[side] = self.available_line_nums.get(side, 0) + 1
  

  # # Calculate line endpoints on square side (CURRENTLY UNUSED)
  # def get_line_endpoints_on_square(self, side_str: str):
  #   num_points = self.line_nums.get(side_str, 0) + 1
  #   side = string_to_direction(side_str)
  #   center = self.get_center()
  #   half_width = self.width / 2
  #   points = []

  #   # Get the directions which determine axis for points
  #   if np.array_equal(side, LEFT) or np.array_equal(side, RIGHT):
  #     low_dir = DOWN
  #     high_dir = UP
  #   else:
  #     low_dir = LEFT
  #     high_dir = RIGHT

  #   # Calculate points equally spread along the side
  #   low_point = center + (side + low_dir) * half_width
  #   for i in range(1, num_points):
  #     point = low_point + (high_dir * self.width * i) / num_points
  #     points.append(point)

  #   return points

  # # (CURRENTLY UNUSED)
  # def get_line_endpoint(self, side: str):
  #   if self.available_line_nums.get(side, 0) > 0:
  #     index = self.line_nums[side] - self.available_line_nums[side]
  #     line_endpoints = self.get_line_endpoints_on_square(side)
  #     self.available_line_nums[side] -= 1
  #     return line_endpoints[index]
