# Django Bulk Copy


### TODO
- [ ] Feat: Create an optional copy model manager.
- [ ] Fix: CSV writer converts empty strings `''` to `null` and it can cause error.
  - There will be a new quoting constants with Python 3.11 ([CPython Issue #67230](https://github.com/python/cpython/issues/67230))
- [ ] Fix: Get the primary key from the latest sequence instead maximum id.
- [ ] Feat: Objects with any type of iterable (like generators) should be accepted.
- [ ] Feat: Make the sequence update an optional operation.
### Completed
- [X] Feat: Update the sequence number after operation.
