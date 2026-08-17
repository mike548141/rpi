- [x] **`read_file(return_scope='lines')` takes a range, not just an index.**
      ✅ Shipped: an int returns one line, a
      `(start, stop[, step])` tuple or a `slice` returns that range joined, and an out-of-range int degrades to `''`
      per the no-traceback contract. The `regex` scope's multi-line return is covered by a test.
