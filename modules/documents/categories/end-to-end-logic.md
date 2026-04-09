# Document Categories — End-to-End Logic

**Module:** Documents
**Feature:** Categories

---

## Create Category

### Flow

```
POST /api/v1/documents/categories
  -> CategoryController.Create(CreateCategoryCommand)
    -> [RequirePermission("documents:manage")]
    -> CategoryService.CreateAsync(command, ct)
      -> 1. Validate: name required, unique within tenant
      -> 2. If parent_category_id provided:
         -> Validate parent exists and belongs to same tenant
         -> Validate max depth (3 levels)
      -> 3. INSERT into document_categories
         -> applies_to: company, department, or employee
      -> Return Result.Success(categoryDto)
```

## List Categories (Hierarchical)

### Flow

```
GET /api/v1/documents/categories
  -> CategoryController.List()
    -> [RequirePermission("documents:read")]
    -> CategoryService.GetTreeAsync(ct)
      -> 1. Query all active categories for tenant
      -> 2. Build tree structure using parent_category_id
      -> Return Result.Success(categoryTree)
```

## Related

- [[frontend/architecture/overview|Categories Overview]]
- [[frontend/architecture/overview|Document Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
