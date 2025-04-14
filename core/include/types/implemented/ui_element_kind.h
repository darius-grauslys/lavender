#ifndef IMPL_UI_ELEMENT_KIND_H
#define IMPL_UI_ELEMENT_KIND_H

#define DEFINE_UI_ELEMENT_KIND

typedef enum UI_Element_Kind {
    UI_Element_Kind__None,
    UI_Element_Kind__Button,
    UI_Element_Kind__Draggable,
    UI_Element_Kind__Slider,
    UI_Element_Kind__Drop_Zone,
    UI_Element_Kind__Logical,
    UI_Element_Kind__Unknown
} UI_Element_Kind;

#endif
