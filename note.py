# Property Management System - Complete API Documentation

## Base URL
```
http://your-domain.com/api/properties/
```

## Authentication
All endpoints require JWT authentication unless specified otherwise.

Include the token in the request header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Table of Contents
1. [Property Endpoints](#property-endpoints)
2. [Bookmark Endpoints](#bookmark-endpoints)
3. [Inspection Endpoints](#inspection-endpoints)
4. [Statistics Endpoint](#statistics-endpoint)

---

# Property Endpoints

## 1. List & Create Properties

### Get All Properties
**Endpoint:** `GET /api/properties/`

**Description:** 
- If user role is `owner`: Returns all their own properties (active + inactive)
- If user role is `buyer`: Returns all active properties

**Authentication:** Required

**Request Headers:**
```http
Authorization: Bearer <token>
```

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Properties retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "slug": "beautiful-house-1",
      "propertyName": "Beautiful House",
      "propertyAddress": "123 Main Street, City",
      "status": true,
      "propertyFeatureImage": "http://domain.com/media/property_feature_images/image.jpg",
      "total_inspection_reports": 2,
      "total_optional_reports": 1,
      "propertyBedrooms": "3",
      "propertyBathrooms": "2",
      "propertyParking": "2",
      "propertyBuildYear": "2020",
      "unlock_price": 10.00,
      "is_unlocked": true,
      "is_bookmarked": false,
      "createdAt": "2026-01-15T10:30:00Z",
      "updatedAt": "2026-01-15T10:30:00Z"
    }
  ]
}
```

---

### Create Property
**Endpoint:** `POST /api/properties/`

**Description:** Create a new property listing

**Authentication:** Required

**Request Headers:**
```http
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```json
{
  "propertyName": "Beautiful House",
  "propertyAddress": "123 Main Street",
  "propertyType": "Residential",
  "propertyBedrooms": "3",
  "propertyBathrooms": "2",
  "propertyParking": "2",
  "propertyBuildYear": "2020",
  "propertyHasPool": true,
  "propertyIsStrataProperty": false,
  "status": true,
  "propertyFeatureImage": <file>,
  "images": [<file1>, <file2>],  // Optional, max 10
  "inspection_reports": [<file1>, <file2>],  // Optional, max 5
  "optional_reports": [<file1>],  // Optional, max 5
  "features": ["Spacious Kitchen", "Garden", "Garage"]  // Optional, max 20
}
```

**Validation Rules:**
- `propertyName`: Required
- `propertyAddress`: Required
- `propertyType`: Required
- `propertyFeatureImage`: Required
- `images`: Max 10 files
- `inspection_reports`: Max 5 files
- `optional_reports`: Max 5 files
- `features`: Max 20 items

**Response (Success - 201):**
```json
{
  "success": true,
  "messgae": "Property created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "slug": "beautiful-house",
    "owner_name": "John Doe",
    "owner_email": "john@example.com",
    "owner_phone": "+1234567890",
    "owner_image": "http://domain.com/media/users/john.jpg",
    "propertyName": "Beautiful House",
    "propertyAddress": "123 Main Street",
    "propertyType": "Residential",
    "propertyBedrooms": "3",
    "propertyBathrooms": "2",
    "propertyParking": "2",
    "propertyBuildYear": "2020",
    "propertyHasPool": true,
    "propertyIsStrataProperty": false,
    "status": true,
    "propertyFeatureImage": "http://domain.com/media/property_feature_images/image.jpg",
    "images": [
      {
        "id": "uuid",
        "image": "http://domain.com/media/property_images/img1.jpg",
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-15T10:30:00Z"
      }
    ],
    "inspection_reports": [],
    "optional_reports": [],
    "features": [
      {
        "id": "uuid",
        "feature": "Spacious Kitchen",
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-15T10:30:00Z"
      }
    ],
    "total_photos": 2,
    "total_inspection_reports": 0,
    "total_optional_reports": 0,
    "total_views": 0,
    "checkboxes_checked": 1,
    "qr_code_url": "http://domain.com/api/properties/beautiful-house/",
    "is_bookmarked": false,
    "createdAt": "2026-01-15T10:30:00Z",
    "updatedAt": "2026-01-15T10:30:00Z"
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "propertyName": ["This field is required."],
    "images": ["Maximum 10 images allowed."]
  }
}
```

---

## 2. Property Detail

### Get Property Details
**Endpoint:** `GET /api/properties/<slug>/`

**Description:** Get detailed information about a specific property (increments view count for non-owners)

**Authentication:** Required

**URL Parameters:**
- `slug` (string): Property slug

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Property retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "slug": "beautiful-house",
    "owner_name": "John Doe",
    "owner_email": "john@example.com",
    "owner_phone": "+1234567890",
    "owner_image": "http://domain.com/media/users/john.jpg",
    "propertyName": "Beautiful House",
    "propertyAddress": "123 Main Street",
    "propertyType": "Residential",
    "propertyBedrooms": "3",
    "propertyBathrooms": "2",
    "propertyParking": "2",
    "propertyBuildYear": "2020",
    "propertyHasPool": true,
    "propertyIsStrataProperty": false,
    "status": true,
    "propertyFeatureImage": "http://domain.com/media/property_feature_images/image.jpg",
    "images": [...],
    "inspection_reports": [...],
    "optional_reports": [...],
    "features": [...],
    "total_photos": 5,
    "total_inspection_reports": 2,
    "total_optional_reports": 1,
    "total_views": 125,
    "checkboxes_checked": 1,
    "qr_code_url": "http://domain.com/api/properties/beautiful-house/",
    "is_bookmarked": false,
    "createdAt": "2026-01-15T10:30:00Z",
    "updatedAt": "2026-01-15T10:30:00Z"
  }
}
```

**Response (Locked Property - 403):**
```json
{
  "success": false,
  "message": "Property is locked. Please unlock to view details.",
  "data": null,
  "errors": {
    "unlocked": true,
    "unlock_price": 10.00,
    "currency": "USD",
    "method": "You need to make a payment to unlock this property."
  }
}
```

**Response (Not Found - 404):**
```json
{
  "success": false,
  "message": "Not found.",
  "data": null,
  "errors": "No Property matches the given query."
}
```

---

### Update Property
**Endpoint:** `PATCH /api/properties/<slug>/`

**Description:** Partially update a property (owner only)

**Authentication:** Required (Owner only)

**URL Parameters:**
- `slug` (string): Property slug

**Request Body (Form Data - All fields optional):**
```json
{
  "propertyName": "Updated Name",
  "status": false,
  "images": [<new_files>],  // Replaces all existing images
  "features": ["New Feature 1", "New Feature 2"]  // Replaces all features
}
```

**Note:** When updating images/reports/features, all existing ones are deleted and replaced with new ones.

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Property updated successfully",
  "data": {
    // Full property details
  }
}
```

---

### Delete Property
**Endpoint:** `DELETE /api/properties/<slug>/`

**Description:** Delete a property (owner only)

**Authentication:** Required (Owner only)

**URL Parameters:**
- `slug` (string): Property slug

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Property 'Beautiful House' deleted successfully",
  "data": null
}
```

---

## 3. Property QR Code

**Endpoint:** `GET /api/properties/<slug>/qr-code/`

**Description:** Generate a QR code for the property

**Authentication:** Required

**URL Parameters:**
- `slug` (string): Property slug

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "QR Code generated successfully",
  "data": {
    "property_name": "Beautiful House",
    "property_address": "123 Main Street",
    "property_url": "http://domain.com/property/beautiful-house/",
    "qr_code": "iVBORw0KGgoAAAANSUhEUgAA..."  // Base64 encoded PNG
  }
}
```

**Usage in Frontend:**
```html
<img src="data:image/png;base64,{qr_code}" alt="QR Code" />
```

---

## 4. Featured Properties

**Endpoint:** `GET /api/properties/featured/list/`

**Description:** Get top 3 most viewed properties

**Authentication:** Not required (Public endpoint)

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Featured properties retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "slug": "property-1",
      "propertyName": "Property 1",
      "total_views": 500,
      // ... other property fields
    },
    {
      "id": "uuid",
      "slug": "property-2",
      "propertyName": "Property 2",
      "total_views": 450,
      // ... other property fields
    },
    {
      "id": "uuid",
      "slug": "property-3",
      "propertyName": "Property 3",
      "total_views": 400,
      // ... other property fields
    }
  ]
}
```

---

# Bookmark Endpoints

## 1. List & Create Bookmarks

### Get All Bookmarks
**Endpoint:** `GET /api/properties/bookmarks/list/`

**Description:** Get all bookmarked properties for the authenticated user

**Authentication:** Required

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Bookmarks retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "property": {
        "id": "uuid",
        "slug": "beautiful-house",
        "propertyName": "Beautiful House",
        "propertyAddress": "123 Main Street",
        "status": true,
        "propertyFeatureImage": "http://domain.com/media/image.jpg",
        "total_inspection_reports": 2,
        "total_optional_reports": 1,
        "propertyBedrooms": "3",
        "propertyBathrooms": "2",
        "propertyParking": "2",
        "propertyBuildYear": "2020",
        "unlock_price": 10.00,
        "is_unlocked": true,
        "is_bookmarked": true,
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-15T10:30:00Z"
      },
      "createdAt": "2026-01-20T14:30:00Z",
      "updatedAt": "2026-01-20T14:30:00Z"
    }
  ]
}
```

---

### Create Bookmark
**Endpoint:** `POST /api/properties/bookmarks/list/`

**Description:** Bookmark a property

**Authentication:** Required

**Request Body:**
```json
{
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "messgae": "Property bookmarked successfully",
  "data": {
    "id": "uuid",
    "property": {
      // Full property details
    },
    "createdAt": "2026-01-20T14:30:00Z",
    "updatedAt": "2026-01-20T14:30:00Z"
  }
}
```

**Response (Already Bookmarked - 400):**
```json
{
  "success": false,
  "message": "Property is already bookmarked",
  "data": null,
  "errors": null
}
```

**Response (Property Not Found - 404):**
```json
{
  "success": false,
  "message": "Property not found",
  "data": null,
  "errors": null
}
```

---

## 2. Delete Bookmark

**Endpoint:** `DELETE /api/properties/bookmarks/<bookmark_id>/`

**Description:** Remove a bookmark

**Authentication:** Required

**URL Parameters:**
- `bookmark_id` (UUID): Bookmark ID

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Bookmark for 'Beautiful House' removed successfully",
  "data": null
}
```

**Response (Not Found - 404):**
```json
{
  "success": false,
  "message": "An error occurred while removing the bookmark",
  "data": null,
  "errors": "No Bookmark matches the given query."
}
```

---

# Inspection Endpoints

## 1. List & Create Inspections

### Get All Inspections
**Endpoint:** `GET /api/properties/inspections/list/`

**Description:** Get all inspection bookings for the authenticated user

**Authentication:** Required

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Inspections retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "property": {
        "id": "uuid",
        "slug": "beautiful-house",
        "propertyName": "Beautiful House",
        // ... other property fields
      },
      "inspection_datetime": "2026-02-15T14:00:00Z",
      "createdAt": "2026-01-20T10:30:00Z",
      "updatedAt": "2026-01-20T10:30:00Z"
    }
  ]
}
```

---

### Create Inspection
**Endpoint:** `POST /api/properties/inspections/list/`

**Description:** Book a property inspection

**Authentication:** Required

**Request Body:**
```json
{
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "inspection_datetime": "2026-02-15T14:00:00Z"
}
```

**Validation:**
- `inspection_datetime` must be in the future
- Property must exist

**Response (Success - 201):**
```json
{
  "success": true,
  "messgae": "Inspection booked successfully",
  "data": {
    "id": "uuid",
    "property": {
      // Full property details
    },
    "inspection_datetime": "2026-02-15T14:00:00Z",
    "createdAt": "2026-01-20T10:30:00Z",
    "updatedAt": "2026-01-20T10:30:00Z"
  }
}
```

**Response (Past Date - 400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "inspection_datetime": ["Inspection date/time must be in the future."]
  }
}
```

**Response (Property Not Found - 404):**
```json
{
  "success": false,
  "message": "Property not found",
  "data": null,
  "errors": null
}
```

---

## 2. Get Inspection Details

**Endpoint:** `GET /api/properties/inspections/<inspection_id>/`

**Description:** Get details of a specific inspection

**Authentication:** Required

**URL Parameters:**
- `inspection_id` (UUID): Inspection ID

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Inspection retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "property": {
      // Full property details
    },
    "inspection_datetime": "2026-02-15T14:00:00Z",
    "createdAt": "2026-01-20T10:30:00Z",
    "updatedAt": "2026-01-20T10:30:00Z"
  }
}
```

---

## 3. Update Inspection

**Endpoint:** `PATCH /api/properties/inspections/<inspection_id>/`

**Description:** Update inspection date/time

**Authentication:** Required

**URL Parameters:**
- `inspection_id` (UUID): Inspection ID

**Request Body:**
```json
{
  "inspection_datetime": "2026-02-20T15:00:00Z"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Inspection updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "property": {
      // Full property details
    },
    "inspection_datetime": "2026-02-20T15:00:00Z",
    "createdAt": "2026-01-20T10:30:00Z",
    "updatedAt": "2026-01-20T15:30:00Z"
  }
}
```

---

## 4. Delete Inspection

**Endpoint:** `DELETE /api/properties/inspections/<inspection_id>/`

**Description:** Cancel/delete an inspection

**Authentication:** Required

**URL Parameters:**
- `inspection_id` (UUID): Inspection ID

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "Inspection for 'Beautiful House' cancelled successfully",
  "data": null
}
```

---

# Statistics Endpoint

## Get User Statistics

**Endpoint:** `GET /api/properties/statistics/user/`

**Description:** Get comprehensive statistics for the authenticated user

**Authentication:** Required

**Response (Success - 200):**
```json
{
  "success": true,
  "messgae": "User statistics retrieved successfully",
  "data": {
    "total_bookmarks": 5,
    "total_inspections": 3,
    "total_properties": 150,
    "bookmarked_properties": [
      {
        "id": "uuid",
        "slug": "property-1",
        "propertyName": "House 1",
        "propertyAddress": "123 Main St",
        "status": true,
        "propertyFeatureImage": "http://domain.com/media/image.jpg",
        "total_inspection_reports": 2,
        "total_optional_reports": 1,
        "propertyBedrooms": "3",
        "propertyBathrooms": "2",
        "propertyParking": "2",
        "propertyBuildYear": "2020",
        "unlock_price": 10.00,
        "is_unlocked": true,
        "is_bookmarked": true,
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-15T10:30:00Z"
      }
    ],
    "upcoming_inspections": [
      {
        "id": "uuid",
        "property": {
          "id": "uuid",
          "slug": "property-2",
          "propertyName": "House 2",
          // ... other property fields
        },
        "inspection_datetime": "2026-02-15T14:00:00Z",
        "createdAt": "2026-01-20T10:30:00Z",
        "updatedAt": "2026-01-20T10:30:00Z"
      }
    ]
  }
}
```

**Statistics Breakdown:**
- `total_bookmarks`: Total number of properties bookmarked by user
- `total_inspections`: Total number of inspections booked by user (all time)
- `total_properties`: Total number of active properties in the entire system
- `bookmarked_properties`: Array of all bookmarked properties with full details
- `upcoming_inspections`: Array of inspections scheduled in the future, ordered by date

---

# Error Responses

All endpoints follow the same error response format:

## Standard Error Response
```json
{
  "success": false,
  "message": "Error message description",
  "data": null,
  "errors": "Detailed error information or validation errors object"
}
```

## Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation errors) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (no permission or locked property) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

# Frontend Integration Examples

## JavaScript/Fetch Examples

### Get All Properties
```javascript
const getProperties = async () => {
  const response = await fetch('http://domain.com/api/properties/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data;
};
```

### Create Bookmark
```javascript
const bookmarkProperty = async (propertyId) => {
  const response = await fetch('http://domain.com/api/properties/bookmarks/list/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      property_id: propertyId
    })
  });
  const data = await response.json();
  return data;
};
```

### Book Inspection
```javascript
const bookInspection = async (propertyId, datetime) => {
  const response = await fetch('http://domain.com/api/properties/inspections/list/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      property_id: propertyId,
      inspection_datetime: datetime  // "2026-02-15T14:00:00Z"
    })
  });
  const data = await response.json();
  return data;
};
```

### Get User Statistics
```javascript
const getUserStats = async () => {
  const response = await fetch('http://domain.com/api/properties/statistics/user/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data;
};
```

### Create Property with Files
```javascript
const createProperty = async (formData) => {
  // formData is a FormData object containing all fields and files
  const response = await fetch('http://domain.com/api/properties/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // Don't set Content-Type, browser will set it with boundary
    },
    body: formData
  });
  const data = await response.json();
  return data;
};

// Usage:
const form = new FormData();
form.append('propertyName', 'Beautiful House');
form.append('propertyAddress', '123 Main St');
form.append('propertyType', 'Residential');
form.append('propertyFeatureImage', imageFile);
form.append('images', imageFile1);
form.append('images', imageFile2);
form.append('features', 'Spacious Kitchen');
form.append('features', 'Garden');

await createProperty(form);
```

---

# Quick Reference

## All Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/properties/` | List properties | ✅ |
| POST | `/api/properties/` | Create property | ✅ |
| GET | `/api/properties/<slug>/` | Get property details | ✅ |
| PATCH | `/api/properties/<slug>/` | Update property | ✅ |
| DELETE | `/api/properties/<slug>/` | Delete property | ✅ |
| GET | `/api/properties/<slug>/qr-code/` | Generate QR code | ✅ |
| GET | `/api/properties/featured/list/` | Get featured properties | ❌ |
| GET | `/api/properties/bookmarks/list/` | List bookmarks | ✅ |
| POST | `/api/properties/bookmarks/list/` | Create bookmark | ✅ |
| DELETE | `/api/properties/bookmarks/<id>/` | Delete bookmark | ✅ |
| GET | `/api/properties/inspections/list/` | List inspections | ✅ |
| POST | `/api/properties/inspections/list/` | Create inspection | ✅ |
| GET | `/api/properties/inspections/<id>/` | Get inspection | ✅ |
| PATCH | `/api/properties/inspections/<id>/` | Update inspection | ✅ |
| DELETE | `/api/properties/inspections/<id>/` | Delete inspection | ✅ |
| GET | `/api/properties/statistics/user/` | Get user statistics | ✅ |

---

# Notes

1. **Date Format:** All datetime fields use ISO 8601 format: `2026-02-15T14:00:00Z`
2. **File Uploads:** Use `multipart/form-data` for endpoints with file uploads
3. **UUID Format:** All IDs are UUIDs (e.g., `550e8400-e29b-41d4-a716-446655440000`)
4. **Pagination:** Currently not implemented, but can be added if needed
5. **Rate Limiting:** Not currently implemented
6. **CORS:** Ensure CORS is configured on your backend for frontend access

---

**Last Updated:** February 2026  
**Version:** 1.0