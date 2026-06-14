class PandocInjector:
    @staticmethod
    def text_sequence(raw_link_text, ref_name, seq_name):
        return (
            f'<text:sequence-ref text:reference-format="value" '
            f'text:sequence-name="{seq_name}" text:ref-name="{ref_name}">'
            f"{raw_link_text}"
            f"</text:sequence-ref>"
        )

    @staticmethod
    def text_sequence_suffix(
        ref_name, full_digit, prefix_text, suffix_text, style_attr, seq_name
    ):
        return (
            f"<text:span{style_attr}>"
            f"{prefix_text}"
            f'<text:sequence-ref text:reference-format="value" '
            f'text:sequence-name="{seq_name}" text:ref-name="{ref_name}">'
            f"{full_digit}"
            f"</text:sequence-ref>"
            f"{suffix_text}"
            f"</text:span>"
        )

    @staticmethod
    def draw_frame(
        caption_text,
        w_str,
        h_str,
        outer_h_str,
        image_tag,
        safe_caption,
        ref_name,
        prefix,
        display_counter,
        style_name,
        formula,
        seq_name,
    ):
        return (
            f'<draw:frame draw:style-name="Graphics" draw:name="{prefix}_{display_counter}" '
            f'text:anchor-type="paragraph" svg:width="{w_str}" style:rel-width="100%" '
            f'svg:height="{outer_h_str}" style:rel-height="scale-min" draw:z-index="{display_counter}">'
            f"<draw:text-box>"
            f'<text:p text:style-name="{style_name}">'
            f'<draw:frame draw:name="Graphic_{safe_caption}" svg:title="{safe_caption}" '
            f'text:anchor-type="paragraph" svg:width="{w_str}" style:rel-width="100%" '
            f'svg:height="{h_str}" style:rel-height="scale" draw:z-index="1">'
            f"{image_tag}"
            f"</draw:frame>"
            f'{prefix} <text:sequence text:ref-name="{ref_name}" text:name="{seq_name}" '
            f'text:formula="{formula}" style:num-format="1">{display_counter}</text:sequence>: {caption_text}'
            f"</text:p>"
            f"</draw:text-box>"
            f"</draw:frame>"
        )
