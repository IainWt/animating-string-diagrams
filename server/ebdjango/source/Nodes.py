from manim import *

  

class Node(VGroup):
  def __init__(self, shape, tex='', tex_color=BLACK, **kwargs):
    super().__init__(**kwargs)
    self.line_nums = {}
    self.available_line_nums = {}
    self.shape = shape
    tex = Tex(tex, color=tex_color).move_to(shape)
    self.add(shape, tex)
    

class ManimSquare(Node):
  def __init__(self, tex='', side_length=1, fill_opacity=1, fill_color=BLUE, stroke_color=BLACK, **kwargs):
    side_length = kwargs.pop('height', side_length)
    side_length = kwargs.pop('width', side_length)
    square = Square(fill_color=fill_color, side_length=side_length, fill_opacity=fill_opacity, stroke_color=stroke_color, **kwargs)
    super().__init__(shape=square, tex=tex, **kwargs)


class ManimRectangle(Node):
  def __init__(self, tex='', height=1, width=1, fill_opacity=1, fill_color=BLUE, stroke_color=BLACK, **kwargs):
    print("fill_opacity", fill_opacity)
    rectangle = Rectangle(fill_color=fill_color, height=height, width=width, fill_opacity=fill_opacity, stroke_color=stroke_color, **kwargs)
    super().__init__(shape=rectangle, tex=tex, **kwargs)


class ManimCircle(Node):
  def __init__(self, tex='', radius=0.5, fill_opacity=1, fill_color=BLUE, stroke_color=BLACK, **kwargs):
    radius = kwargs.pop('height', radius)
    radius = kwargs.pop('width', radius)
    circle = Circle(radius=radius, fill_color=fill_color, fill_opacity=fill_opacity, stroke_color=stroke_color, **kwargs)
    super().__init__(shape=circle, tex=tex, **kwargs)


class InvisibleDot(Node):
  def __init__(self, tex='', fill_opacity=0, **kwargs):
    dot = Dot( fill_opacity=fill_opacity, **kwargs)
    super().__init__(shape=dot, tex=tex, **kwargs)


class ManimMorphism(Node):
  def __init__(self, tex='', size=1, fill_color=BLUE, stroke_color=BLACK, fill_opacity=1, **kwargs):
    size = kwargs.pop('height', size)
    size = kwargs.pop('width', size)
    vertices = [[-0.5, 0.35, 0], [0.5, 0.35, 0], [0.8, -0.35, 0], [-0.5, -0.35, 0]]
    vertices = [np.array(vertex) * size for vertex in vertices]
    polygon = Polygon(*vertices, fill_color=fill_color, fill_opacity=fill_opacity, stroke_color=stroke_color, **kwargs)
    super().__init__(shape=polygon, tex=tex, **kwargs)




def create_and_position_node(node):
  shape = create_shape(node.label, **node.props)
  shape.move_to(node.position)
  return shape


def create_shape(label, shape='square', **other_props):
  if shape == 'none':
    return InvisibleDot(label, **other_props)
  if shape == 'square':
    return ManimSquare(label, **other_props)
  if shape == 'rectangle':
    return ManimRectangle(label, **other_props)
  if shape == 'circle':
    return ManimCircle(label, **other_props)
  if shape == 'morphism':
    return ManimMorphism(label, **other_props)
  if shape == 'dot':
    return ManimCircle(label, radius=0.1, **other_props)