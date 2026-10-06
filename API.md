# TMS Adapter API Documentation

HTTP/JSON wrapper for Legacy TMS (Tramway) TCP communication. Bridges voice agents with freight management system.

**Base URL:** `https://tms-adapter-production-a2b8.up.railway.app`

**Authentication:** All protected endpoints require `Authorization: Bearer <API_KEY>` header

---

## Endpoints

### 1. GET `/`

**Description:** Service status endpoint

**Authentication:** Not required

**Request:**
```bash
curl https://tms-adapter-production-a2b8.up.railway.app/
```

**Response (200 OK):**
```json
{
  "status": "TMS Adapter ready"
}
```

---

### 2. GET `/health`

**Description:** Check TMS connection health and adapter status

**Authentication:** Not required

**Request:**
```bash
curl https://tms-adapter-production-a2b8.up.railway.app/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "tms": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "error": "Connection failed: [error details]"
}
```

---

### 3. POST `/loads/search`

**Description:** Search for available loads on the TMS open board

**Authentication:** Required (`Authorization: Bearer <API_KEY>`)

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "GA",
    "destination": "TX",
    "equipment": "DRY_VAN"
  }' \
  https://tms-adapter-production-a2b8.up.railway.app/loads/search
```

**Request Body:**
```json
{
  "origin": "GA",              // State code (required)
  "destination": "TX",         // State code (required)
  "equipment": "DRY_VAN"       // Equipment type: DRY_VAN, REEFER, FLATBED, etc. (required)
}
```

**Response (200 OK) - Loads Found:**
```json
{
  "loads": [
    {
      "LOAD_ID": "LD0000045821",
      "ORIG_CITY": "Atlanta",
      "ORIG_STATE": "GA",
      "ORIG_ZIP": "30303",
      "DEST_CITY": "Dallas",
      "DEST_STATE": "TX",
      "DEST_ZIP": "75201",
      "PICKUP_DT": "20260512080000",
      "EQTYPE": "DRY_VAN",
      "RATE": "0002150",
      "MILES": "000785",
      "STATUS": "OPEN"
    }
  ],
  "count": 1
}
```

**Response (200 OK) - No Loads Found:**
```json
{
  "loads": [],
  "count": 0
}
```

**Response (400 Bad Request) - Missing Filter:**
```json
{
  "error": "ERR|CODE:MISSING_FIELD|MSG:at least one filter required"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Unauthorized"
}
```

**Response (503 Service Unavailable):**
```json
{
  "error": "Connection failed to TMS: [error details]"
}
```

---

### 4. GET `/loads/<load_id>`

**Description:** Retrieve full details for a specific load

**Authentication:** Required (`Authorization: Bearer <API_KEY>`)

**Request:**
```bash
curl -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  https://tms-adapter-production-a2b8.up.railway.app/loads/LD0000045821
```

**URL Parameters:**
- `load_id` (string, required): Load identifier (e.g., `LD0000045821`)

**Response (200 OK) - Load Found:**
```json
{
  "LOAD_ID": "LD0000045821",
  "ORIG_CITY": "Atlanta",
  "ORIG_STATE": "GA",
  "ORIG_ZIP": "30303",
  "DEST_CITY": "Dallas",
  "DEST_STATE": "TX",
  "DEST_ZIP": "75201",
  "PICKUP_DT": "20260512080000",
  "DELIVERY_DT": "20260514090000",
  "EQTYPE": "DRY_VAN",
  "RATE": "0002150",
  "WEIGHT": "5500",
  "COMMODITY": "General Freight",
  "PIECES": "12",
  "MILES": "000785",
  "DIMS": "48ft x 8ft x 9ft",
  "NOTES": "Standard pickup. Standard delivery.",
  "STATUS": "OPEN",
  "MAX_BUY": "2500"
}
```

**Response (400 Bad Request) - Load Not Found:**
```json
{
  "CODE": "NOT_FOUND",
  "MSG": "Load not found"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Unauthorized"
}
```

**Response (503 Service Unavailable):**
```json
{
  "error": "Connection failed to TMS: [error details]"
}
```

---

### 5. POST `/loads/<load_id>/book`

**Description:** Book a load (placeholder - not yet implemented)

**Authentication:** Required (`Authorization: Bearer <API_KEY>`)

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  https://tms-adapter-production-a2b8.up.railway.app/loads/LD0000045821/book
```

**URL Parameters:**
- `load_id` (string, required): Load identifier to book

**Response (501 Not Implemented):**
```json
{
  "message": "Booking not yet implemented"
}
```

---

## Data Structures

### Load Object

Field name descriptions and formats:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| LOAD_ID | String | Unique load identifier | LD0000045821 |
| ORIG_CITY | String | Origin city | Atlanta |
| ORIG_STATE | String | Origin state code | GA |
| ORIG_ZIP | String | Origin ZIP code | 30303 |
| DEST_CITY | String | Destination city | Dallas |
| DEST_STATE | String | Destination state code | TX |
| DEST_ZIP | String | Destination ZIP code | 75201 |
| PICKUP_DT | String | Pickup date/time (YYYYMMDDhhmmss) | 20260512080000 |
| DELIVERY_DT | String | Delivery date/time (YYYYMMDDhhmmss) | 20260514090000 |
| EQTYPE | String | Equipment type | DRY_VAN, REEFER, FLATBED |
| RATE | String | Rate offered (in dollars, padded) | 0002150 |
| WEIGHT | String | Load weight (lbs, padded) | 5500 |
| COMMODITY | String | Commodity description | General Freight |
| PIECES | String | Number of pieces/pallets | 12 |
| MILES | String | Distance in miles | 000785 |
| DIMS | String | Dimensions | 48ft x 8ft x 9ft |
| NOTES | String | Special instructions/notes | Standard pickup |
| STATUS | String | Load status | OPEN, BOOKED, CANCELLED |
| MAX_BUY | String | Maximum rate the shipper will pay | 2500 |

---

## Equipment Types

Valid equipment type values:

- `DRY_VAN` - Standard dry trailer
- `REEFER` - Refrigerated trailer
- `FLATBED` - Flatbed trailer
- `TANKER` - Tanker truck
- `SPECIALIZED` - Specialized equipment

---

## Error Codes

TMS may return the following error codes:

| Code | Description |
|------|-------------|
| AUTH_FAILED | Invalid or missing authentication token |
| UNKNOWN_CMD | Command not recognized |
| MISSING_FIELD | Required field missing from request |
| NOT_FOUND | Load ID not found |
| ALREADY_BOOKED | Load has already been booked |
| INVALID_RATE | Rate is outside acceptable range |
| MALFORMED | Request format is invalid |
| SERVER_ERROR | TMS server error |

---

## Authentication

### API Key

All protected endpoints require an `Authorization` header with a bearer token:

```bash
Authorization: Bearer <API_KEY>
```

**Example:**
```bash
curl -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  https://tms-adapter-production-a2b8.up.railway.app/loads/LD0000045821
```

**Response if missing or invalid:**
```json
{
  "error": "Unauthorized"
}
```

HTTP Status: `401 Unauthorized`

---

## Rate Limiting

No explicit rate limiting is enforced, but the underlying TMS may have connection limits. Adapter maintains one connection per request (TMS closes after each response).

---

## Timeouts

- **Connection timeout:** 6 seconds
- **Response timeout:** 2 seconds per request
- **Idle timeout:** 30 seconds (server-initiated close)

---

## Example Usage

### Search for available loads

```bash
curl -X POST \
  -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "GA",
    "destination": "TX",
    "equipment": "DRY_VAN"
  }' \
  https://tms-adapter-production-a2b8.up.railway.app/loads/search
```

### Get specific load details

```bash
curl -H "Authorization: Bearer happyrobot-fde-secret-key-12345" \
  https://tms-adapter-production-a2b8.up.railway.app/loads/LD0000045821
```

### Check service health

```bash
curl https://tms-adapter-production-a2b8.up.railway.app/health
```

---

## Implementation Notes

- All timestamps use format `YYYYMMDDhhmmss`
- State codes must be 2-character abbreviations (GA, TX, FL, etc.)
- Equipment types are case-sensitive uppercase
- Numeric fields are space-padded on the right (fixed width)
- Field order in responses may vary across TMS versions
- The adapter uses the TMS token from environment variables (`TMS_TOKEN`)
- Each TMS request opens a fresh connection (connection reuse not supported)

---

## Support

For issues or questions:
- Check TMS connection: `GET /health`
- Review logs on Railway dashboard
- Verify API key is correct
- Ensure TMS host and port are accessible
