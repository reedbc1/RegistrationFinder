# AddressLookup (Library Patron Registration Helper)

## Problem & Context

Public library staff must determine the correct **geographic code** and **patron type** when registering a new library card.

Before this tool, staff had to manually cross-reference multiple external systems—often in sequence—to determine eligibility:

- USPS or mapping tools to validate addresses  
- County real estate or GIS sites to determine jurisdiction  
- School district data to infer eligibility in certain counties  

This process was time-consuming, error-prone, and required staff to understand complex geographic rules that vary by county.

---

## Solution Overview

**AddressLookup** is a back-end–driven web application that automates this decision process.

Staff enter a street address and ZIP code, and the system:

- Validates the address  
- Infers geographic jurisdiction  
- Applies county-specific eligibility rules  
- Returns a clear, actionable result for registration  

The goal is to reduce cognitive load, eliminate manual lookups, and ensure consistent registration outcomes.

---

## Tech Stack

- **Language:** Python  
- **Backend:** Flask (REST-style request handling)  
- **APIs & Data Sources:**  
  - United States Census Bureau – Census Geocoder  
  - Google Maps Geocoding API (fallback)  
  - County GIS data via ArcGIS Feature Services  
- **Data Storage:** CSV-based reference data for patron types and eligibility rules  
- **Deployment:** Render  

---

## Architecture & Request Flow

1. Staff submits a street address and ZIP code via a web form  
2. Backend normalizes and validates the input  
3. Address is geocoded using Census data (primary source)  
4. If Census validation fails, Google Maps is used as a fallback  
5. Geographic jurisdiction is inferred from geocoded coordinates  
6. County-specific logic determines patron type and eligibility  
7. Results are returned to the client in a structured format  

---

## Eligibility & Decision Logic

- **County-level inference**  
  If eligibility can be determined at the county (or city) level alone, the system returns a result without further geographic checks.

- **St. Louis County**  
  The system determines which library district the address contributes taxes to using county GIS boundary data.

- **Jefferson County**  
  Eligibility is inferred based on the school district associated with the residence.

- **Ineligible addresses**  
  If the address does not fall into any eligible jurisdiction, it is marked as ineligible.  

---

## Output

### Primary Results
- Standardized address  
- Geographic code  
- Patron type  

### Supporting Details
- County (or city, when applicable)  
- Library district (St. Louis County)  
- School district (Jefferson County)  

Primary results provide the actionable information required for patron registration. Supporting details explain how the program arrived at the result. This increases transparency and trust in the program’s decision logic for staff and makes it easy to manually validate.  

---

## Tradeoffs & Limitations

- **API cost control**  
  Google Maps is used only as a fallback to limit external API usage and cost.

- **Data freshness**  
  CSV reference files require manual updates when eligibility rules or boundaries change.

- **Boundary precision**  
  Apartment-level granularity is intentionally ignored to reduce ambiguity in GIS boundaries.

- **Dependency on GIS accuracy**  
  Results depend on the accuracy of county-provided GIS datasets.

These tradeoffs balance maintainability, reliability, and operational simplicity.

---

## Future Improvements
- Add ArcGIS geocoding API as additional fallback for higher traffic
- Add library district info for other counties
- Add audit logging for registration decisions
- Expose the logic as a versioned internal API  

---

## Deployment

The application is deployed and accessible online:

https://registrationfinder.onrender.com/
