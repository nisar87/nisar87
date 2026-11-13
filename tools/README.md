# How the profile images are made

`python3 tools/build.py` redraws everything in `assets/` (needs `pip install fonttools brotli`).

- Product names, taglines, colours and status come from `tools/products.json`. Edit that file, or copy the values from the website's `content/products.mjs`, then run the script again.
- Text is drawn as shapes, so the images look the same everywhere without loading fonts.
