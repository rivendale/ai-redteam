# An incremental iOS build 3 minutes faster with a Library cache  (post, 2026-09-14)

On one 60-scene project, a warm incremental iOS build took a median of 14 minutes without a cache for the Library folder and 11 minutes with one (10 runs each,
same Mac mini, same commit; the runs were interleaved). The Android build was not measured. The cache is a tarball of Library/ restored before the build.

| Run set | Median build | Range |
|---|---|---|
| no Library cache | 14 min | 13-15 |
| Library cache | 11 min | 10-12 |
