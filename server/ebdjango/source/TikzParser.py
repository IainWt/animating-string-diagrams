from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
import re

"""
TikZ Parser should take as input:

--- Nodes ---
- style
- id 
- position
- label
e.g. node [style=white square] (0) at (-7.25, 0) {$a$};

--- Lines ---
- in & out angles, looseness
- start node id (maybe id.center)
- end node id (maybe id.center)
e.g. draw [in=-180, out=0, looseness=0.75] (5.center) to (2);

### OUTPUT ###

TikzDiagram class instance - contains:
- node class instances
- line class instances
- styles as dictionaries of style name & properties


"""

class Location():
  def __init__(self, location: str) -> None:
    self.type = None
    self.location = self.parse_location(location)

  def parse_location(self, location: str):
      """Clean endpoint to remove '.center' or extract coordinates"""
      if location.endswith(".center"):
        self.type = 'id'
        return location[:-7]
      if ',' in location:
        self.type = 'coordinate'
        coords_tuple = re.findall(r"(.+), (.+)", location)[0]
        return float(coords_tuple[0]), float(coords_tuple[1])
      if '.' in location:
        self.type = 'compass'
        id, direction = location.split('.')
        return {'id': id, 'direction': direction}
      self.type = 'id'
      return location
  
  def __repr__(self) -> str:
    return f"Location(type={self.type}, location={self.location})"


@dataclass
class TikzNode():
  style: str
  id: str
  position: Tuple[float, float]
  label: str


@dataclass
class TikzLine():
  start_loc: Union[str, Tuple[float]]
  end_loc: str
  in_angle: float
  out_angle: float
  looseness: float


@dataclass
class TikzDiagram():
  nodes: List[TikzNode]
  lines: List[TikzLine]
  styles: Dict[str, Dict[str, str]]


class TikzParser():

  @staticmethod
  def parse_nodes(tikz) -> List[TikzNode]:
    """Return all nodes from TikZ code"""
    node_pattern = r"\\node\s*\[(.+)\] \((.+)\) at \((.+)\) \{(.*)\}"
    matches = re.findall(node_pattern, tikz)
    nodes = []
    for match in matches:
      style, id, position_str, label, = match
      if style.startswith('style='): style = style[6:]
      position_tuple = re.findall(r"(.+), (.+)", position_str)[0]
      position = (float(position_tuple[0]), float(position_tuple[1]))
      node = TikzNode(style, id, position, label)
      nodes.append(node)
    return nodes
  

  @staticmethod
  def clean_endpoint(location: str):
      """Clean endpoint to remove '.center' or extract coordinates"""
      if location.endswith(".center"): return location[:-7]
      if ',' in location:
        coords_tuple = re.findall(r"(.+), (.+)", location)[0]
        return float(coords_tuple[0]), float(coords_tuple[1])
      return location


  @staticmethod
  def parse_lines(tikz) -> List[TikzLine]:
    """Return all nodes from TikZ code"""
    line_pattern = r"\\draw[^\\;]+;"
    line_matches = re.findall(line_pattern, tikz)
    
    lines = []
    for line_str in line_matches:
      curve_props_pattern = r"\[(.+)\]"
      curve_props_match = re.search(curve_props_pattern, line_str)
      curve_props = curve_props_match.group() if curve_props_match else ''

      # Curve properties
      curve_prop_values = []
      for match_word in ['in', 'out', 'looseness']:
        search_string = r"(?<=" + match_word + r"=)\-?\d+(\.\d+)?"
        matched_value = re.search(search_string, curve_props)
        curve_prop_values.append(matched_value.group() if matched_value else None)

      in_angle, out_angle, looseness = curve_prop_values
      if in_angle: in_angle = float(in_angle)
      if out_angle: out_angle = float(out_angle)
      if looseness: looseness = float(looseness)

      # Endpoints
      endpoints_pattern = r"\((.+)\)\sto[^\\;\(]+\((.+)\);"
      endpoints_match = re.search(endpoints_pattern, line_str)
      if endpoints_match == None:
        raise Exception("Invalid line endpoints: ", line_str)
      start_loc_str, end_loc_str = endpoints_match.groups()
      start_loc = Location(start_loc_str)
      end_loc = Location(end_loc_str)

      # If property is bend left/right
      bend_pattern = r"(?<=bend )([a-z]+)=(-?\d+(\.\d+)?)"
      bend_match = re.search(bend_pattern, curve_props)
      #   - if left: correct out_angle      - if right: -angle is out_angle
      #   - if left: 180-angle is in_angle  - if right: -180+angle is in_angle
      if bend_match:
        bend_dir, bend_angle = bend_match.group(1), float(bend_match.group(2))
        if bend_dir == 'left':
          out_angle = bend_angle
          in_angle = 180 - bend_angle
        elif bend_dir == 'right':
          out_angle = -bend_angle
          in_angle = -180 + bend_angle
        else:
          raise Exception("Bend direction must be left or right")

      line = TikzLine(start_loc, end_loc, in_angle, out_angle, looseness)
      lines.append(line)
    
    return lines


  def parse_styles(tikz) -> Dict[str, Dict[str,str]]:
    """Parse all styles from a tikzstyles text"""
    styles = {'morphism': {'shape': 'morphism'}, 'dot': {'shape': 'dot'}}
    style_pattern = r"(?<!% )\\tikzstyle\{(.+)\}=\[(.+)\]"
    style_matches = re.findall(style_pattern, tikz)
    for name, props_str in style_matches:
      props_pattern = r"(\w[^,]*)=([^,]+)"
      props_matches = re.findall(props_pattern, props_str)
      styles[name] = dict(props_matches)
    return styles


  @staticmethod
  def parse_tikz_diagram(tikz, tikz_styles):
    """Parse all nodes and lines from a diagram"""
    nodes = TikzParser.parse_nodes(tikz)
    lines = TikzParser.parse_lines(tikz)
    styles = TikzParser.parse_styles(tikz_styles)
    return TikzDiagram(nodes, lines, styles)
  

### FOR TESTING ###
if __name__ == "__main__":

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
      \node [style=white square] (1) at (-5.75, 0) {$b$};
      \node [style=white square] (2) at (-4.25, 1) {$2$};
      \node [style=white square] (3) at (-2.75, 1) {};
      \node [style=white square] (4) at (-5.75, -1) {};
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
    \end{pgfonlayer}"""

  TikzParser.parse_tikz_diagram(test_tikz, test_styles)
  freetikz_line = TikzParser.parse_lines(r"\draw (m0.south east) to [out=-90, in=90] (6.25, 1.8);")
  freetikz_node = TikzParser.parse_nodes(r"\node [morphism] (m0) at (-5.75, 0) {m0};")
  print(freetikz_line)
  print(freetikz_node)





