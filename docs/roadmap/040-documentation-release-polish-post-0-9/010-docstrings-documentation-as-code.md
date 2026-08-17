- [x] **Docstrings (documentation-as-code).** ✅ Done: every function with a leading `#` comment now carries a
      `"""docstring"""` (converted by a one-off transform, reviewed by hand), and the public entry points that had
      no lead comment (`main`, `parse_args`, the `render_*` family, `f_num`, `term_width`, `cleanup`) got a
      hand-written one-liner. `pydoc` / `help()` / any API-doc generator now shows the intent, not just signatures.
      Every *public* function is documented; a handful of trivial private helpers (`_pread`, `_open_read`, …) that
      never had a lead comment are left bare by design.
