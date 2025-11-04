# Conversion Tools

This directory contains tools for converting research data into JSON listings.

## convert_research.py

Converts markdown research files into JSON listings following schema v1.0.

### Usage

```bash
# Dry run (preview what would be created)
python3 scripts/conversion/convert_research.py research_file.md --dry-run

# Convert and save listings
python3 scripts/conversion/convert_research.py research_file.md

# Specify custom output directory
python3 scripts/conversion/convert_research.py research_file.md --output-dir /path/to/output
```

### Features

- **Automatic parsing** of markdown research files
- **Schema v1.0 compliance** with all required fields
- **Auto-fill** of metadata, dates, and schema version
- **Tag inference** from text markers (⭐ MAJOR PLAYER, organic, sustainable, etc.)
- **Category detection** from filename
- **Dry-run mode** for previewing output
- **Batch conversion** of multiple suppliers from one file

### Expected Research Format

The tool expects research files with supplier sections formatted like:

```markdown
#### 1. Company Name ⭐ MAJOR PLAYER
- **Website:** https://example.com
- **Location:** 123 Main St, City, State ZIP, Country
- **Phone:** 555-123-4567
- **Specializations:** Product 1, Product 2, Product 3
- **Product Focus:** Description of products
- **Tags:** tag1, tag2, tag3
- **Notes:** Additional information
- **Strategic Importance:** Why this supplier matters
```

### Output

Creates JSON files in the appropriate category directory with this structure:
```
listings/
  Raw_Materials/
    Emollients_Moisturizers/
      1828_company_name.json
```

### What Gets Extracted

From markdown research, the tool extracts:
- Company name (cleaned of markers like ⭐)
- Website URL
- Address and country
- Phone number
- Specializations (as array)
- Product highlights (as array)
- Tags (from explicit tags or inferred from text)
- Notes and strategic importance
- Metadata (source file, validation date, etc.)

### What Gets Auto-Generated

- `schema_version`: Always "1.0"
- `listing_id`: Generated from company name
- `category_id`: Inferred from filename or defaulted
- `category_path`: Inferred from filename or defaulted  
- `url`: Generated based on category
- `status`: Always "active"
- `date_added`: Current date
- `date_updated`: Current date
- `metadata`: Validation metadata with source file

### Category Detection

The tool infers categories from filenames:
- `emollients` → Raw_Materials/Emollients_Moisturizers
- `botanical` → Raw_Materials/Botanical_Extracts
- `preservatives` → Raw_Materials/Preservatives
- `surfactants` → Raw_Materials/Surfactants
- `actives` → Raw_Materials/Actives
- `packaging` or `bottles_jars` → Packaging/Bottles_and_Jars
- `tubes` → Packaging/Tubes
- `contract_manufacturing` → Business_Services/Contract_Manufacturing
- And more...

### Tag Inference

The tool automatically infers tags from text:
- `⭐ MAJOR PLAYER` → adds "major-player" tag
- `⭐ MANUFACTURER` → adds "contract-manufacturer" tag
- "organic" in text → adds "natural-ingredients" tag
- "sustainable" in text → adds "sustainable" tag
- "distributor" or "global" → adds "global-distributor" tag

### Example

```bash
# Convert emollients research
python3 scripts/conversion/convert_research.py research_emollients_2025-11-04.md --dry-run

# Output shows:
# Found 15 suppliers
# Inferred category: Raw_Materials/Emollients_Moisturizers
# Would create: 1828_cargill_beauty.json, 1828_basf_beauty.json, etc.
```

### Next Steps After Conversion

1. **Review** the generated JSON files
2. **Fill in** any missing information (address, phone, certifications)
3. **Validate** with `python3 scripts/validation/validate_listings.py`
4. **Commit** the new listings

### Limitations

- Requires research files to follow the expected markdown format
- Category inference may not work for all filename patterns
- Some manual review and enhancement recommended after conversion
- Missing fields (address, phone, etc.) need to be filled in manually if not in research

### Tips for Best Results

1. **Use consistent markdown format** in research files
2. **Include all key fields** in research (Website, Location, Phone, Specializations, etc.)
3. **Use markers** like ⭐ MAJOR PLAYER to enable auto-tagging
4. **Name files descriptively** to enable category detection (e.g., `research_emollients_2025-11-04.md`)
5. **Review dry-run** output before actual conversion
6. **Validate** after conversion to catch any issues

---

**Status:** ✅ Ready for use  
**Version:** 1.0  
**Last Updated:** November 4, 2025
