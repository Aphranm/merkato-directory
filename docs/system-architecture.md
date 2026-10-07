# System architecture and product blueprint

## Product definition

Merkato Directory is a digital directory for businesses physically located inside Merkato. Its primary purpose is to help a person find a business from incomplete information and determine its exact location.

## Core location model

- Building
- Floor
- Unit / room / stall
- Business

The business should not be permanently tied to a single physical location. A first-class `BusinessLocation` relation enables a business to occupy multiple rooms or branches.

## Core entity model

- User
- Role
- Building
- Floor
- Unit
- Business
- Category
- BusinessCategory
- BusinessLocation
- Contact
- Image
- Report
- Verification
- AuditLog

## Experience split

### Public directory

- Search and filter businesses
- Browse buildings, categories, and units
- View business pages with location breadcrumbs
- Read contact info based on consent and visibility rules
- Report incorrect information
- Share URLs

### Administrative system

- Manage buildings, floors, units, businesses, and categories
- Control verification and publication
- Upload and organize images
- Manage permissions and users
- Review reports and audit history
- Detect duplicates and archive stale entries

## Core functional phases

1. Foundation
2. Admin management
3. Public directory
4. Quality control
5. Production hardening
6. Growth features

## Architectural rules

- Model relationships, not a single nested tree
- Treat categories as independent from physical hierarchy
- Use soft delete / archive patterns instead of hard delete for directory data
- Use server-side authorization and not client-only UI hiding
- Search should be backed by a real API rather than frontend-only logic
- Pagination, filters, and ranking should be part of the core API contract

## Operational priorities

- Mobile-first public experience
- Search and zero-result analytics
- Validation and duplicates
- Backup and restore process
- Audit trails for admin activity
- Access control and role model

## Minimum first production definition

The first usable production version should support:

- creating and editing data
- archiving and publishing
- valid relationships
- image uploads
- search and filter
- location breadcrumbs
- permissions
- reporting incorrect information
- audit logs
- duplicate detection

This is the source of truth for the next implementation milestones.
