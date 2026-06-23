# Exoplanet Archive

> **In plain terms:** Programmatic access to NASA's catalog of confirmed planets and candidates outside our solar system. You write filter queries against the database — e.g., planets in the Kepler field or small, temperate candidates — aimed at research and planet-hunting analysis.

## Introduction

The Exoplanet Archive API allows programatic access to NASA's Exoplanet Archive database. This API contains a ton of options so to get started please visit this page for introductory materials. To see what data is available in this API visit here and also be sure to check out best-practices and troubleshooting in case you get stuck. Happy planet hunting!

## Example Queries

| Example API | URL |
|-------------|-----|
| Confirmed planets in the Kepler field | `https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?&table=exoplanets&format=ipac&where=pl_kepflag=1` |
| Confirmed planets that transit their host stars | `https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?&table=exoplanets&format=ipac&where=pl_tranflag=1` |
| All planetary candidates smaller than 2Re with equilibrium temperatures between 180-303K | `https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&where=koi_prad<2 and koi_teq>180 and koi_teq<303 and koi_disposition like 'CANDIDATE'` |
