# oc.snapshot

**oc.snapshot** is a powerful sidecar for **oc.user**, enabling the capture and preservation of the user environment's state at any given moment. By leveraging this functionality, users can create detailed snapshots of their entire environment, including configurations, data, and active processes, ensuring a consistent and reliable record of their system's condition. This capability is particularly valuable for troubleshooting, system audits, or rapid recovery in case of errors, as it allows teams to revert to a stable state or analyze past configurations without manual intervention. With **oc.snapshot**, the user environment becomes not only more manageable but also more resilient, offering a robust solution for maintaining data integrity and operational continuity.

## API

The **oc.snapshot** sidecar exposes an HTTP API for managing snapshots. The API is accessible at `http://<sidecar_ip>:29785`. Below are some of the available endpoints and their functionalities:
- **POST /snapshot**: Creates a new snapshot of the current environment. The response will include details about the created snapshot.


Certainly! Here's a **professional English version** of how to document your REST API in a `README.md` file, tailored to your Python source code:


### `GET /version`

**Description**: Returns the current version of the API.

**Response Example**:

```json
{
  "status": "success",
  "message": "version is 1.0.0"
}
```

### 🔹 `POST /snapshot`

**Description**: Captures a snapshot of the current system state and pushes the resulting image to the container registry.

**Success Response**:

```json
{
  "status": "success",
  "message": "image pushed to registry"
}
```

**Error Response**:

```json
{
  "status": "error",
  "message": "error <description>"
}
```

### `GET /swagger` or `GET /swagger.json`

**Description**: Returns the Swagger (OpenAPI) specification describing the available API endpoints.

**Response**: A Swagger JSON object generated from `swagger/swagger.yaml`.


### `404 Not Found`

**Description**: Returned when the requested endpoint does not exist.

**Response Example**:

```json
{
  "status": "error",
  "message": "unsupported page"
}
```

## 🛠️ Possible Errors

* `500` – Failed to load or parse the Swagger YAML file.
* `200` with `"status": "error"` – Typically returned if a `nerdctl` operation fails during `/snapshot`.

---

## Development tests

To get the current version of the API, run:

~~~bash
curl -X POST http://localhost:29785/version
~~~

To run a manual snapshot, you can use the following command:

~~~bash
curl -X POST http://localhost:29785/snapshot
~~~