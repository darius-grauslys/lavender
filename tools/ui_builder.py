from pyglet import shapes
import string
import pyglet
from pyglet.gl import glEnable
from pyglet.gl import glBlendFunc
from pyglet.gl import GL_BLEND
from pyglet.gl import GL_SRC_ALPHA
from pyglet.gl import GL_ONE_MINUS_SRC_ALPHA
from pyglet import image
import xml.etree.ElementTree as ET
import sys
import os
import re
from collections import deque

def get_mtime_if__file_exists__else_return_0(path):
    return os.path.getmtime(path) if os.path.exists(path) else 0

def get_str_from_xml_or__use_this(xml_node, term, default):
    return default \
            if term not in xml_node.attrib \
            else xml_node.attrib[term]

def get_int_from_xml_or__use_this(xml_node, term, default):
    return default \
            if term not in xml_node.attrib \
            else int(xml_node.attrib[term])

def get_int_tuple_from_xml_or__use_this(xml_node, term, default):
    return default \
            if term not in xml_node.attrib \
            else tuple(map(int, xml_node.attrib[term] \
                    .split(',')))

class Include:
    def __init__(self, path):
        self.path = path

class Background:
    def __init__(self, path, layer, x, y):
        self.path = path
        self.image = None if path == "" else image.load(path)
        if self.image != None:
            self.image.format = 'RGBA'
            rawimage = self.image.get_image_data()
            #rawimage.format = 'RGBA'
            format = 'RGBA'
            pitch = rawimage.width * len(format)
            pixels = bytearray(rawimage.get_data(format, pitch))
            for i in range((len(pixels) // 4) - 1):
                if pixels[i*4] == 0xff and pixels[i*4+2] == 0xff:
                    pixels[i*4+3] = 0x0
                else:
                    pixels[i*4+3] = 0xff
            rawimage.set_data(format, pitch, bytes(pixels))
        self.layer = layer
        self.modification_time = get_mtime_if__file_exists__else_return_0(path)
        self.x = x
        self.y = y

class Config:
    def __init__(self, path_to__source_xml):
        self.is_visualizing = True
        self.BACKEND = "PLATFORM"
        self.signatures = []
        self.source_xml = path_to__source_xml
        self.source_name = os.path.splitext(\
                os.path.basename(self.source_xml))[0]
        self.associated_header_sub_dir_in__include_folder=""
        self.output__c_path = "./output.c"
        self.output__h_path = "./output.h"
        self.window_size = (256, 256)
        self.backgrounds = [Background("", 0, 0, 0), Background("", 1, 0, 0), Background("", 2, 0, 0), Background("", 3, 0, 0)]
        self.includes = []
        self.base_dir="./"
        self.is_outputting = True

    def update_from__xml_node(self, xml_node):
        self.includes = []
        for element in xml_node:
            if element.tag == "ui_func_signature":
                self.signatures.append(UI_Signature(\
                        get_str_from_xml_or__use_this(element, "for", ""),\
                        get_str_from_xml_or__use_this(element, "c_signatures", "")\
                        ))
            if element.tag == "platform":
                self.BACKEND = get_str_from_xml_or__use_this(element, "target", self.BACKEND)
                self.window_size = get_int_tuple_from_xml_or__use_this(element, "size", self.window_size)
                window.set_size(self.window_size[0], self.window_size[1])
            if element.tag == "output":
                self.base_dir = get_str_from_xml_or__use_this(element, "base_dir", self.base_dir)
                self.output__c_path = get_str_from_xml_or__use_this(element, "c_path", self.output__c_path)
                self.output__h_path = get_str_from_xml_or__use_this(element, "h_path", self.output__h_path)
            if element.tag == "background":
                layer = next((i for i, b in enumerate(self.backgrounds) if b.image == None), self.backgrounds[0])
                layer = get_int_from_xml_or__use_this(element, "layer", layer)
                self.backgrounds[layer] = Background(\
                        get_str_from_xml_or__use_this(element, "path", None), \
                        layer,\
                        get_int_from_xml_or__use_this(element, "x", 0),\
                        get_int_from_xml_or__use_this(element, "y", 0))
            if element.tag == "include":
                self.associated_header_sub_dir_in__include_folder = \
                        get_str_from_xml_or__use_this(element, "sub_dir", "")
                for header in element:
                    self.includes.append(Include(\
                            get_str_from_xml_or__use_this(header, "path", None)))

if len(sys.argv) < 2:
    print("Give source xml")
    quit()

if not os.path.exists(sys.argv[1]):
    print("Cannot find source xml.")
    quit()

config = Config(sys.argv[1])

modification_time = os.path.getmtime(config.source_xml)

p_ui_manager="p_ui_manager"
p_ui_iterator="p_ui_iterator"
PLATFORM = "PLATFORM"
squares = []
source_c=""
source_h=""
tab="    "
error=""
current_element_id=0

def set_error(msg):
    global error
    error = msg

if len(sys.argv) >= 3:
    for index in [i*2 + 2 for i in range(0, (len(sys.argv)-2) // 2)]:
        try:
            field = getattr(config, sys.argv[index])
            if isinstance(field, bool):
                setattr(config, sys.argv[index], sys.argv[index+1].lower() == "true")
            elif isinstance(field, int):
                setattr(config, sys.argv[index], int(sys.argv[index+1]))
        except IndexError:
            set_error("Missing argument for config field: {}".format(sys.argv[index]))
            break
        except AttributeError as exception:
            set_error("{} is not a valid config field.".format(exception))
            break

window = pyglet.window.Window(\
        width=config.window_size[0], \
        height=config.window_size[1], \
        visible=config.is_visualizing)
label__error = pyglet.text.Label('', \
        font_name='Times New Roman', \
        font_size=36, \
        x=0, y=0, width=config.window_size[0], height=36, color=(255, 55, 55, 255))

def update_label__error(msg):
    global label__error
    label__error = pyglet.text.Label(msg, \
            font_name='Times New Roman', \
            font_size=1.5 * config.window_size[0]/(len(msg)+1), \
            x=0, y=0, width=config.window_size[0], height=36, color=(255, 55, 55, 255))

def get_y(y, height):
    return window.height - y - height

class UI_Signature:
    def __init__(self, xml_tag, c_signatures):
        self.xml_tag = xml_tag
        self.c_signatures = c_signatures.split(',')
        self.callback = globals()[xml_tag]

class Context:
    def __init__(self, x, y, \
            stride__x, stride__y, \
            position, quantity_of__elements):
        self.x = x
        self.y = y
        self.stride__x = stride__x
        self.stride__y = stride__y
        self.position = position
        self.quantity_of__elements = quantity_of__elements
        self.index_of__iteration = ""
        self.index_of__element = 0
        self.quantity_of__sub_elements = 0
        self.indentation_level = 0
        self.p_ui_element = ""

    @classmethod
    def allocate_context_from__xml_element(cls, xml_element, context_stack):
        context = cls( \
            context_stack[-1].x \
            + context_stack[-1].stride__x \
            * context_stack[-1].index_of__element \
            + (0
                if "x" not in xml_element.attrib \
                else int(xml_element.attrib["x"])), \
            context_stack[-1].y \
            + context_stack[-1].stride__y \
            * context_stack[-1].index_of__element \
            + (0
                if "y" not in xml_element.attrib \
                else int(xml_element.attrib["y"])), \
            0 \
                if "stride__x" not in xml_element.attrib \
                else int(xml_element.attrib["stride__x"]), \
            0 \
                if "stride__y" not in xml_element.attrib \
                else int(xml_element.attrib["stride__y"]), \
            context_stack[-1].position \
                if "position" not in xml_element.attrib \
                else tuple(map(int, xml_element.attrib["position"] \
                        .split(','))), \
            get_int_from_xml_or__use_this(xml_element, "size", 1) \
                )
        context.indentation_level = context_stack[-1].indentation_level
        return context

class RectangleSpec:
    def __init__(self, xml_element, context_stack):
        self.x = 0 \
                if "x" not in xml_element.attrib \
                else int(xml_element.attrib["x"])
        self.y = 0 \
                if "y" not in xml_element.attrib \
                else int(xml_element.attrib["y"])
        self.width = 0 \
            if "width" not in xml_element.attrib \
            else int(xml_element.attrib["width"])
        self.height = 0 \
            if "height" not in xml_element.attrib \
            else int(xml_element.attrib["height"])
        self.color = get_int_tuple_from_xml_or__use_this(\
                xml_element, "color", (55,55,55))

def generate_source_h__with_literal(literal):
    global source_h
    source_h += literal

def generate_source_h__named_ui_index(name, unique_id):
    generate_source_h__with_literal(\
            "#define {0}_{1}_{2} {2}".format(\
                config.source_name.upper(),\
                name.upper(),\
                unique_id))

def generate_source_c__tabs(quantity_of__tabs):
    global source_c
    source_c += tab * quantity_of__tabs

def stringify(value):
    return (value if value is string else str(value))

def generate_source__arguments(args, source_c_or__source_h):
    global source_c
    global source_h
    if source_c_or__source_h:
        source_c += "("
        if len(args) == 0:
            source_c += ")"
            return
        for i in range(len(args) - 1):
            source_c += stringify(args[i]) + ", "
        source_c += stringify(args[-1])
        source_c += ")"
    else:
        source_h += "("
        if (len(args) == 0):
            source_h += ")"
            return
        for i in range(len(args) - 1):
            source_h += stringify(args[i]) + ", "
        source_h += stringify(args[-1])
        source_h += ")"

def generate_source_c__arguments(args):
    generate_source__arguments(args, True)

def generate_source_h__arguments(args):
    generate_source__arguments(args, False)

def generate_source_c__signature(signature, args):
    global source_c
    source_c += signature.c_signatures[0]
    generate_source_c__arguments(args)

def generate_source_c__new_line():
    global source_c
    source_c += ";\n"

def generate_source_c__with_literal(literal):
    global source_c
    source_c += literal

def generate_source_c__local_field__p_ui_element(name_of__ui_element):
    global source_c
    source_c += "UI_Element *{} = ".format(name_of__ui_element)

def get_source_string__struct_field__p_next(ui_element_alias):
    return "{}->p_next".format(ui_element_alias)

def generate_source_c__local_assignment__iterator():
    generate_source_c__with_literal("{} = ".format(p_ui_iterator))

def generate_source_c__local_assignment__iterator_with__literal(literal):
    generate_source_c__with_literal("{}{} = ".format(p_ui_iterator, literal))

def get_source_string__loop__iterator(context_stack):
    return "index_of__iteration__{}".format(len(context_stack) - 1)

def generate_source_c__loop_begin__for(literal__index, literal__comparison, literal__increment):
    generate_source_c__with_literal(\
            "for (Index__u32 {0}=0;{1};{2},{0}++) {{\n".format(\
            literal__index, literal__comparison, literal__increment))
def generate_source_c__loop_end__for(context_stack):
    generate_source_c__with_literal("}\n")

def generate_source_c__include(include):
    generate_source_c__with_literal("#include <{}>".format(include.path))

def generate_source_h__named_ui_index_if__has_name(xml_element):
    name = get_str_from_xml_or__use_this(xml_element, "name", None)
    if name is not None:
        generate_source_h__named_ui_index(name, current_element_id)
        generate_source_h__with_literal("\n")

def allocate_square(x, y, width, height, color):
    squares.append(shapes.Rectangle(\
            x=x, y=get_y(y, height), width=width, height=height, color=color))

def allocate_many_squares_with__context_stack(rectangle_spec, context_stack):
    for i in range(context_stack[-1].quantity_of__elements):
        allocate_square(\
                rectangle_spec.x \
                    + context_stack[-1].x \
                    + i * context_stack[-1].stride__x \
                    - rectangle_spec.width / 2, \
                rectangle_spec.y \
                    + context_stack[-1].y \
                    + i * context_stack[-1].stride__y \
                    - rectangle_spec.height / 2, \
                rectangle_spec.width, \
                rectangle_spec.height, \
                rectangle_spec.color)

def allocate_ui(signature, xml_element, context_stack):
    global current_element_id
    context_stack.append(Context.allocate_context_from__xml_element(\
            xml_element, context_stack))
    name = get_str_from_xml_or__use_this(xml_element, "name", p_ui_iterator)
    generate_source_h__named_ui_index_if__has_name(xml_element)
    generate_source_c__tabs(context_stack[-1].indentation_level)
    if name != p_ui_iterator:
        generate_source_c__local_field__p_ui_element(name)
    else:
        generate_source_c__local_assignment__iterator()
    context_stack[-1].p_ui_element = name
    generate_source_c__signature(signature, [p_ui_manager])
    generate_source_c__new_line()
    for sub_xml_element in xml_element:
        generate_source_c__tabs(context_stack[-1].indentation_level)
        construct_ui_from__xml_element(sub_xml_element, context_stack)
    context_stack.pop()
    current_element_id += context_stack[-1].quantity_of__elements

def generate_source_c__iteration_by__succession(context_stack):
    context_stack[-1].index_of__iteration = \
            get_source_string__loop__iterator(context_stack)
    generate_source_c__loop_begin__for(\
            get_source_string__loop__iterator(context_stack),\
            p_ui_iterator,\
            "iterate_to_next__ui_element(&{})".format(\
                p_ui_iterator))

def get_unique_id_for__element(context_stack):
    id = 0
    for context in context_stack:
        id += context.index_of__element + context.quantity_of__sub_elements
    return id

def group(signature, xml_element, context_stack):
    context = Context.allocate_context_from__xml_element(\
            xml_element, context_stack)
    context_stack.append(context)
    generate_source_h__named_ui_index_if__has_name(xml_element)
    for sub_xml_element in xml_element:
        construct_ui_from__xml_element(sub_xml_element, context_stack)
        generate_source_c__with_literal("\n")
    context_stack[-2].quantity_of__sub_elements += context_stack.pop().quantity_of__elements

def grid(signature, xml_element, context_stack):
    context = Context.allocate_context_from__xml_element(\
            xml_element, context_stack)
    context_stack.append(context)
    generate_source_h__named_ui_index_if__has_name(xml_element)
    last_index = -1;
    for _ in range(context.quantity_of__elements):
        for sub_xml_element in xml_element:
            construct_ui_from__xml_element(sub_xml_element, context_stack)
            generate_source_c__with_literal("\n")
        if -1 != last_index:
            generate_source_c__tabs(context_stack[-1].indentation_level)
            generate_source_c__local_assignment__iterator_with__literal("_previous_previous->p_next")
            generate_source_c__with_literal("get_p_ui_element_by__index_from__ui_manager({},{})"\
                    .format(p_ui_manager, \
                    last_index\
                    ))
            generate_source_c__new_line()
        generate_source_c__tabs(context_stack[-1].indentation_level)
        generate_source_c__local_assignment__iterator_with__literal("_previous_previous")
        generate_source_c__with_literal("{}{}".format(p_ui_iterator, "_previous"))
        generate_source_c__new_line()
        last_index = current_element_id;
    context_stack[-2].quantity_of__sub_elements += context_stack.pop().quantity_of__elements

def alloc_child(signature, xml_element, context_stack):
    global current_element_id
    context_stack[-1].index_of__element -= 1
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_assignment__iterator_with__literal("_child")
    generate_source_c__signature(signature, [p_ui_manager, p_ui_iterator])
    generate_source_c__new_line()
    context_stack[-1].p_ui_element = "{}{}".format(p_ui_iterator, "_child")
    for sub_xml_element in xml_element:
        generate_source_c__tabs(context_stack[-1].indentation_level)
        construct_ui_from__xml_element(sub_xml_element, context_stack)
    current_element_id += context_stack[-1].quantity_of__elements

def allocate_ui_container(signature, xml_element, context_stack):
    global current_element_id
    context = Context.allocate_context_from__xml_element(\
            xml_element, context_stack)
    generate_source_h__named_ui_index_if__has_name(xml_element)
    context_stack.append(context)
    size = context.quantity_of__elements
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_assignment__iterator()
    generate_source_c__signature(signature, [p_ui_manager, size])
    generate_source_c__new_line()
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__iteration_by__succession(context_stack)
    context_stack[-1].indentation_level += 1
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_assignment__iterator_with__literal("_previous")
    generate_source_c__with_literal(p_ui_iterator)
    generate_source_c__new_line()
    for sub_xml_element in xml_element:
        # reset the p_ui_element in case we iterated in to a sub_container.
        context_stack[-1].p_ui_element = p_ui_iterator
        generate_source_c__tabs(context_stack[-1].indentation_level)
        construct_ui_from__xml_element(sub_xml_element, context_stack)
    current_element_id += size
    context_stack[-1].indentation_level -= 1
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__loop_end__for(context_stack)
    context_stack[-2].quantity_of__sub_elements += context_stack.pop().quantity_of__elements

def get_rect_spec_args(context_stack, rectangle_spec):
    iteration_multiplication_string = \
            "" if context_stack[-1].index_of__iteration == ""\
            else "* {}".format(context_stack[-1].index_of__iteration)
    return [\
            rectangle_spec.width, rectangle_spec.height,\
            "get_vector__3i32({}, {}, {})".format(\
                "{} + {}{}".format(\
                    rectangle_spec.x + context_stack[-1].x, \
                    context_stack[-1].stride__x, \
                    iteration_multiplication_string), \
                "{} + {}{}".format(
                    rectangle_spec.y + context_stack[-1].y, \
                    context_stack[-1].stride__y, \
                    iteration_multiplication_string), \
                0)\
        ]

def get_vector_3i32_argument(\
        context_stack, xml_element, \
        x_str, y_str, z_str,\
        x_offset, y_offset, z_offset):
    x = \
            get_str_from_xml_or__use_this(\
                xml_element, \
                x_str, \
                "0")
    y = \
            get_str_from_xml_or__use_this(\
                xml_element, \
                y_str, \
                "0")
    z = \
            get_str_from_xml_or__use_this(\
                xml_element, \
                z_str, \
                "0")
    return "get_vector__3i32({}, {}, {})".format(\
            "{} + {}".format(\
                x, \
                x_offset), \
            "{} + {}".format(\
                y, \
                y_offset), \
            "{} + {}".format(\
                z, \
                z_offset) \
            )\

def background(signature, xml_element, context_stack):
    rectangle_spec = RectangleSpec(xml_element, context_stack)

    args = []
    args.append(context_stack[-1].p_ui_element)
    args += get_rect_spec_args(context_stack, rectangle_spec)
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "p_gfx_window", \
                "0"))

    generate_source_c__signature(\
            signature,\
            args)
    
    generate_source_c__new_line()
    # TODO: do a transparent rect that is opaque dotted outline
    # allocate_many_squares_with__context_stack(rectangle_spec, context_stack)

def button(signature, xml_element, context_stack):
    rectangle_spec = RectangleSpec(xml_element, context_stack)

    args = []
    args.append(context_stack[-1].p_ui_element)
    args += get_rect_spec_args(context_stack, rectangle_spec)
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "m_Clicked_Handler", \
                "m_ui_button__clicked_handler__default"))
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "is_toggleable", \
                "false"))
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "is_toggled", \
                "false"))

    generate_source_c__signature(\
            signature,\
            args)
    
    generate_source_c__new_line()
    allocate_many_squares_with__context_stack(rectangle_spec, context_stack)

def slider(signature, xml_element, context_stack):
    rectangle_spec = RectangleSpec(xml_element, context_stack)

    args = []
    args.append(context_stack[-1].p_ui_element)
    args += get_rect_spec_args(context_stack, rectangle_spec)
    args.append(get_vector_3i32_argument(\
            context_stack,\
            xml_element,\
            "spanning_width",\
            "spanning_height",\
            "spanning_depth",\
            "0", "0", "0"))
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "m_Dragged_Handler", \
                "m_ui_slider__dragged_handler__default"))
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "snapped_x_or__y", \
                "true"))

    generate_source_c__signature(\
            signature,\
            args)
    
    generate_source_c__new_line()
    allocate_many_squares_with__context_stack(rectangle_spec, context_stack)

def draggable(signature, xml_element, context_stack):
    rectangle_spec = RectangleSpec(xml_element, context_stack)

    args = []
    args.append(context_stack[-1].p_ui_element)
    args += get_rect_spec_args(context_stack, rectangle_spec)
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "m_Dragged_Handler", \
                "m_ui_draggable__dragged_handler__default"))

    generate_source_c__signature(\
            signature,\
            args)
    
    generate_source_c__new_line()
    allocate_many_squares_with__context_stack(rectangle_spec, context_stack)

def drop_zone(signature, xml_element, context_stack):
    rectangle_spec = RectangleSpec(xml_element, context_stack)

    args = []
    args.append(context_stack[-1].p_ui_element)
    args += get_rect_spec_args(context_stack, rectangle_spec)
    args.append(\
            get_str_from_xml_or__use_this(\
                xml_element, \
                "m_Receive_Drop_Handler", \
                "m_ui_drop_zone__receive_drop_handler__default"))

    generate_source_c__signature(\
            signature,\
            args)
    
    generate_source_c__new_line()
    allocate_many_squares_with__context_stack(rectangle_spec, context_stack)

def code(signature, xml_element, context_stack):
    statements = list(filter(None, re.split("\n *", xml_element.text)))
    generate_source_c__with_literal(statements[0].format(context_stack[-1].p_ui_element))
    generate_source_c__with_literal("\n")
    if 1 == len(statements):
        return
    for statement in statements[1:]:
        generate_source_c__tabs(context_stack[-1].indentation_level)
        generate_source_c__with_literal(statement.format(context_stack[-1].p_ui_element))
        generate_source_c__with_literal("\n")

def construct_ui_from__xml_element(xml_element, context_stack):
    matched_signature = list(filter(\
                lambda x:x.xml_tag == xml_element.tag, config.signatures))
    if matched_signature == []:
        print("unknown element: {}".format(xml_element.tag))
        return
    matched_signature[0].callback(matched_signature[0], xml_element, context_stack)
    context_stack[-1].index_of__element += 1

def generate_source__ui(xml_node__ui):
    global current_element_id
    config.includes.insert(0, Include("{}{}.h".format(\
            config.associated_header_sub_dir_in__include_folder,\
            config.source_name)))
    for include in config.includes:
        generate_source_c__include(include)
        generate_source_c__with_literal("\n")
    
    generate_source_h__with_literal(\
            "#ifndef {}_H\n".format(config.source_name.upper()))
    generate_source_h__with_literal(\
            "#define {}_H\n".format(config.source_name.upper()))
    generate_source_h__with_literal(\
            "\n#include <defines.h>\n".format(config.BACKEND.upper(), config.source_name.upper()))
    generate_source_h__with_literal(\
            "// THIS CODE IS AUTO GENERATED. Go to ./core/assets/ui/xml/ instead of modifying this file.\n")
    generate_source_h__with_literal(\
            "\nbool allocate_ui_for__{}".format(\
            config.source_name))
    generate_source_h__arguments(["Gfx_Context *p_gfx_context, Graphics_Window *p_gfx_window, Game *p_game, UI_Manager *p_ui_manager"])
    generate_source_h__with_literal(";\n")

    generate_source_c__with_literal(\
            "// THIS CODE IS AUTO GENERATED. Go to ./core/assets/ui/xml/ instead of modifying this file.\n")
    generate_source_c__with_literal(\
            "\nbool allocate_ui_for__{}".format(\
            config.source_name))
    generate_source_c__arguments(["Gfx_Context *p_gfx_context, Graphics_Window *p_gfx_window, Game *p_game, UI_Manager *p_ui_manager"])
    generate_source_c__with_literal("{\n")

    context_stack = deque()
    context_stack.append(Context(0, 0, 0, 0, (0,0,0), 1))
    context_stack[-1].indentation_level = 1
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_field__p_ui_element(p_ui_iterator)
    generate_source_c__with_literal("0")
    generate_source_c__new_line()
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_field__p_ui_element("{}{}".format(p_ui_iterator, "_previous_previous"))
    generate_source_c__with_literal("0")
    generate_source_c__new_line()
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_field__p_ui_element("{}{}".format(p_ui_iterator, "_previous"))
    generate_source_c__with_literal("0")
    generate_source_c__new_line()
    generate_source_c__tabs(context_stack[-1].indentation_level)
    generate_source_c__local_field__p_ui_element("{}{}".format(p_ui_iterator, "_child"))
    generate_source_c__with_literal("0")
    generate_source_c__new_line()
    current_element_id = get_int_from_xml_or__use_this(xml_node__ui, "offset_of__ui_index", 0)
    for element in xml_node__ui:
        construct_ui_from__xml_element(element, context_stack)
    generate_source_c__with_literal("return true;\n")
    generate_source_c__new_line()
    generate_source_c__with_literal("}\n")
    generate_source_h__with_literal("#endif\n")


def read_ui(path):
    global source_c
    global source_h
    source_c = ""
    source_h = ""
    tree = 0
    root = 0
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as exception:
        set_error("Error reading xml: {}".format(exception.position))
        return
    set_error('')
    xml_node__config = root.find("config")
    xml_node__ui = root.find("ui")
    if xml_node__config is None:
        print("xml is missing config node.")
        quit()
    if xml_node__ui is None:
        print("xml is missing ui node.")
        quit()
    try:
        config.update_from__xml_node(xml_node__config)
    except FileNotFoundError as exception:
        set_error("File missing: {}".format(exception.filename))
        return
    try:
        generate_source__ui(xml_node__ui)
    except KeyError as exception:
        set_error("Missing field: {}".format(exception))
        return
    if config.is_outputting:
        text_file = open(\
                os.path.join(config.base_dir, config.output__c_path), "w")
        text_file.write(source_c)
        text_file.close()
        text_file = open(\
                os.path.join(config.base_dir, config.output__h_path), "w")
        text_file.write(source_h)
        text_file.close()

@window.event
def on_draw():
    global modification_time
    global error
    window.clear()
    glEnable(GL_BLEND)
    if error != "":
        update_label__error(error)
        error=""
    new_modification_time = get_mtime_if__file_exists__else_return_0(config.source_xml)
    if modification_time < new_modification_time:
        modification_time = new_modification_time
        squares.clear()
        read_ui(config.source_xml)
    for background in config.backgrounds:
        new_modification_time = get_mtime_if__file_exists__else_return_0(\
                background.path)
        if background.modification_time < new_modification_time:
            config.backgrounds[background.layer] = Background(\
                    os.path.join(config.base_dir, background.path), background.layer,\
                    config.backgrounds[background.layer].x,\
                    config.backgrounds[background.layer].y \
                    )
        if background.image is not None:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            background.image.blit(background.x,\
                    window.height - background.y - background.image.height,0)
    for square in squares:
        square.draw()
    if label__error.text != '':
        label__error.x = config.window_size[0] / 2  - label__error.width / 3
        label__error.y = config.window_size[1] / 2  - label__error.height / 2
        label__error.draw()

if label__error.text == '':
    read_ui(config.source_xml)

if config.is_visualizing:
    pyglet.app.run()
