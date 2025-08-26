# File & Path Routing

The foundation of MockHub's routing is a direct mapping from the HTTP request line to the filesystem.

---

## Method → Directory

Each HTTP method has a corresponding directory inside a service folder (e.g., `GET/`, `POST/`, `PUT/`). MockHub looks for a response file within the directory that matches the incoming request's method.

This allows you to serve different payloads for the same path, depending on the HTTP verb used. For example:
* `GET /users/1` could be served from `GET/users/1.json`
* `PUT /users/1` could be served from `PUT/users/1.json`

---

## Path → File

The request path maps directly to a file or directory path.

* `GET /user/repos` → looks for `GET/user/repos.json`
* A trailing slash maps to an `_index` file: `GET /issues/` → looks for `GET/issues/_index.json`
* The root path (`/`) maps to `_index`: `GET /` → looks for `GET/_index.json`

If you request a path with a specific file extension (e.g., `/data.csv`, `/styles.css`), MockHub will look for a file with that exact name and extension. If no extension is provided, **`.json` is assumed by default**.

---

## Content-Type Inference

MockHub automatically sets the `Content-Type` header based on the payload file's extension. This is covered in more detail in the [Content Types](../reference/content-types.md) reference.
