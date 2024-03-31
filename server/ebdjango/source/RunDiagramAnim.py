import sys
from manim import *
from .DiagramAnim import DiagramScene


def split_list(input_list, length):
  return [input_list[i:i + length] for i in range(0, len(input_list), length)]

def read_tikz_and_style_files(tikz_loc, style_loc):
  with open(tikz_loc, 'r') as tikz_file, open(style_loc, 'r') as style_file:
    tikz_content = tikz_file.read()
    style_content = style_file.read()
  return tikz_content, style_content

def render_animation_from_files(tikz_type, style_file_path, tikz_file_paths):
  if tikz_type == 'tikzit':
    tikz_and_style_pairs = [read_tikz_and_style_files(tikz_file_path, style_file_path) for tikz_file_path in tikz_file_paths]

  else: raise Exception("Freetikz not ready yet")

  config.quality = "low_quality"
  scene = DiagramScene(tikz_and_style_pairs)
  scene.render()


def render_animation(tikz_type, style_content, tikz_contents_list, extra_info):
  if tikz_type == 'tikzit':
    tikz_and_style_pairs = [(tikz_content, style_content) for tikz_content in tikz_contents_list]

  else: raise Exception("Freetikz not ready yet")

  config.quality = "low_quality"
  scene = DiagramScene(tikz_and_style_pairs, extra_info=extra_info)
  scene.render()



if __name__ == '__main__':
  """Run Diagram animation from command line"""
  # args in format: -tikz_type -s style_file tikz_file tikz_file ...
  args = sys.argv[1:]

  tikz_type = args[0][1:]
  assert tikz_type in ['tikzit', 'freetikz'], "You must include a tikz type flag: -tikzit or -freetikz"

  if tikz_type == 'tikzit':
    assert args[1] == '-s', "You must include a style file"
    style_file = args[2]
    tikz_files = args[3:]

    tikz_and_style_pairs = [read_tikz_and_style_files(tikz_file, style_file) for tikz_file in tikz_files]

  else: raise Exception("Freetikz not ready yet")

  config.quality = "low_quality"
  config.preview = True

  scene = DiagramScene(tikz_and_style_pairs)
  scene.render()



  