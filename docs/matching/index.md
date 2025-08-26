# Request Matching Overview

MockHub uses a layered system to match incoming HTTP requests to the correct response. The resolution happens in a specific order of precedence: **Hooks → Rules → Filesystem**.

This section covers the different ways you can define how requests are matched.

1.  **[File & Path Routing](files-and-paths.md)**: The most basic form of matching, based on the request method and path mapping directly to directories and files.

2.  **[Query Strings](query-strings.md)**: How to serve different responses based on URL query parameters.

3.  **[Body Predicates](body-predicates.md)**: A simple way to vary responses based on a key-value pair in a JSON request body.

4.  **[Rules](rules.md)**: A declarative YAML format for matching on a combination of method, path, query, and body.

5.  **[Path Wildcards](wildcards.md)**: How to capture dynamic segments from a request path.

For fully dynamic or programmatic matching, see [Python Hooks](../features/hooks.md).
