# web-scrapping-pepper 🌶 (https://www.pepper.pl/)
Final project for Web-scrapping classes on DSBA
To - do:
- [x] bypass "accept cookies" prompt
- [ ] extract bargain info to df
  - [x] extract hottness
  - [x] extract comments
  - [x] extract title
  - [ ] extract price before and after discount
    - [x] extract price values
    - [ ] parse prices to one format
      - [ ] 'ZA DARMO'
      - [ ] prices with '.' as separator (thousands or decimal)
      - [ ] prices with ',' as separator
      - [ ] x % instead of price
      - [ ] 'Allegro Okaze' or similar instead of price value
  - [x] extract username
  - [x] extract link
  - [ ] extract company name (e.g. Allegro okaze, selgros okazje and so on)
- [ ] extract category of bargain (after entering bargain link, on the top part of page there is grey bar with categories) - maybe extract them all in form of category main: something, subcategory: something_2 (if subcategory doesnt exist -> None)
- [x] scan multiple pages
- [ ] create notebook with stats of scrapped pages
- [ ] issue with \<!-- buffered --> - pages are not scrapped if this comment is present
