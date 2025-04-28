#include "platform_defaults.h"
#include <input/input.h>

void initialize_input(Input *p_input) {
    memset(p_input, 0, sizeof(Input));
}

unsigned char poll_input_for__writing(Input *p_input) {
    char symbol = p_input->writing_buffer[
        p_input->index_of__writing_buffer__read];
    if (!symbol) return symbol;
    p_input->last_symbol = symbol;
    p_input->writing_buffer[
        p_input->index_of__writing_buffer__read] = 0;
    p_input->index_of__writing_buffer__read = (
            p_input->index_of__writing_buffer__read + 1)
        & MASK(MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER__BIT_SHIFT);
    return symbol;
}

void buffer_input_for__writing(
        Input *p_input,
        char symbol) {
    p_input->writing_buffer[p_input->index_of__writing_buffer__write] = symbol;
    p_input->index_of__writing_buffer__write = (
            p_input->index_of__writing_buffer__write + 1)
        & MASK(MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER__BIT_SHIFT);
}
