# TechTransfer

> **In plain terms:** Searchable access to NASA's patents, software, and "spinoff" technologies available for public use. Query by keyword to find patents, how they were issued, software, or spinoff examples — aimed at companies and developers wanting to license or build on NASA tech.

NASA's Technology Transfer Program ensures that innovations developed for exploration and discovery are broadly available to the public. The NASA patent portfolio is available to benefit US citizens. Through partnerships and licensing agreements with industry, these patents ensure that NASA's investments in pioneering research find secondary uses that benefit the economy, create jobs, and improve quality of life. This endpoint provides structured, searchable developer access to NASA's patents, software, and technology spinoff descriptions that have been curated to support technology transfer. More information can be found at [technology.nasa.gov](https://technology.nasa.gov) and [software.nasa.gov](https://software.nasa.gov) and [spinoff.nasa.gov](https://spinoff.nasa.gov).

## HTTP Request

`GET https://api.nasa.gov/techtransfer`

## Query Parameters

| Parameter | Type | Default | Description |
|---------------|--------|---------|-------------|
| patent | string | None | Return a JSON of patents that match the string provided |
| patent_issued | string | None | Returns patent results in a JSON that match the string within the information about how issued each patent |
| software | string | None | Returns JSON of NASA software that matches given string. |
| Spinoff | string | None | Returns spinoff examples that match given word. |

## Example query

```
https://api.nasa.gov/techtransfer/patent/?engine&api_key=DEMO_KEY
```
