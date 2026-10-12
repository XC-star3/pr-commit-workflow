# Commit message format

Use a repository-supported Conventional Commit style when one exists:

```text
<type>(<scope>): <imperative summary>

What: ...
Why: ...
Test: ...

Tests: ...
Review: human-approved | ai-reviewed
Risks: ...
```

The subject describes the change. What describes the result, Why describes the need, and Test records the checks and their outcomes. Keep each field specific enough that a maintainer can understand the change without reading the entire diff. Do not claim a test, review, issue link, or user intent that did not occur.
